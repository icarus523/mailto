#!/usr/bin/python3

import webbrowser
import json
import os
import sys
import subprocess
import TemplateEditor
import tkinter as tk
import getpass
import io

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from urllib.parse import quote
from mailtodata import * 
from MailtoManage import MailtoManage

# v0.4b - fixes non re-initialization of the body and subject variables after pressing "Clear Form" button
# v0.5 - Adds To: and Bcc: options, Now has Template Generation within the form. 
# v0.5a - Adds Refresh Template Button to both Systems and Other pages
# v0.6 - 
# v0.6a - Fixes launching of other helper scripts from within mailto.py
#       - backups of lookup JSON file
# v0.6b - Adds a Menu Item to display the URL link to click on.
# v0.6c - Adds a Menu Item to copy_recipients_to_clipboard
#       - Changed reference from FM14 to INET
#       - Added checks for template being selected
# v0.7  - Added version display of emaildata.json 
#       - Added option to disable hashing of emaildata.json and lookup

VERSION = "0.7"
DEFAULT_SUBJECT = "[ENTER EMAIL SUBJECT]"
DEFAULT_BODY = "[This is an output email from 'mailto' script!]\n\n\n"
DEFAULT_COMBO_TEXTBOX = '1. Select a Template...'

USE_ENCODED_DATA = False

# Do not make changes to this, this is default data and is used to 
# re-create the emaildata.json file if one is not already available in the 
# current directory. 
DEFAULT_EMAIL_DATA = {
   "QALAB":[
        "someguy@qalab.com.au"
    ],
    "Technical Requirements":[
        "joeblow@home.net",
        "jane.dow@work.net",
        "here.there@work.net"
    ]
}

class ScrollableFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.vscrollbar.pack(side='right', fill="y",  expand="false")
        self.canvas = tk.Canvas(self, bd=0,
                                height=350,
                                highlightthickness=0,
                                yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side="left", fill="both", expand="true")
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = tk.Frame(self.canvas, **kwargs)
        self.canvas.create_window(0, 0, window=self.interior, anchor="nw")

        self.bind('<Configure>', self.set_scrollregion)


    def set_scrollregion(self, event=None):
        """ Set the scroll region on the canvas"""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

class mailto:

    def __init__(self):
        self.urlstr = ''
        self.path_to_templates = "templates/"
        self.template_subject = DEFAULT_SUBJECT
        self.template_body = DEFAULT_BODY

        self.email_lookup_table = self.ReadJSONfile("emaildata_lookup.json")

        if USE_ENCODED_DATA: 
            self.filename = "emaildata_v2.json"
            self.filename_emaildata_lookup_file = "emaildata_lookup.json"
        else: 
            self.filename = "sample_converted.json"

        self.root = tk.Tk()       
        self.nb = ttk.Notebook(self.root)
       
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        optionmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        menubar.add_cascade(label="Options", menu=optionmenu)
        optionmenu.add_command(label="Launch MailtoManage Group Editor...", command=self.MenuBar_Manage_EmailGroup) 
        optionmenu.add_command(label="Backup Email Group JSON files...", command=self.Backup_EmailFile) 
        optionmenu.add_command(label="Display Mailto URL string...", command=self.Display_URL)
        optionmenu.add_command(label="Copy mailto recipients to clipboard...", command=self.copy_recipients_to_clipboard)        
        filemenu.add_command(label="Exit mailto script", command=self.root.destroy)
        
        self.root.config(menu=menubar)
        self.data = self.ReadJSONfile(self.filename)  
        
        self.setupEGM_Page()
        self.setupOther_Page()
        self.setupSystems_Page()
        self.root.mainloop()    


    def copy_recipients_to_clipboard(self):
        key = self.nb.tab(self.nb.select(), "text").upper()
        print(key, self.urlstr)
        # self.generateEmail(key.upper()) # self.urlstr update

        recipients = ''
        cc = ''
        bcc = '' 
        
        if key == "EGM":
            recipients = self.text_TOoutput_EGM.get(1.0, END)
            cc = self.text_CCoutput_EGM.get(1.0, END)
            bcc = self.text_BCCoutput_EGM.get(1.0, END)

            subject = self.template_subject
            body = self.template_body

            template = self.combobox_box_Template_EGM.get()
                
        elif key == "OTHER":
            recipients = self.text_TOoutput_OTHER.get(1.0, END)
            cc = self.text_CCoutput_OTHER.get(1.0, END)
            bcc = self.text_BCCoutput_OTHER.get(1.0, END)
            
            subject = self.template_subject
            body = self.template_body

            template = self.combobox_box_Template_OTHER.get()
            
        elif key == "SYSTEMS":
            recipients = self.text_TOoutput_SYS.get(1.0, END)
            cc = self.text_CCoutput_SYS.get(1.0, END)
            bcc = self.text_BCCoutput_SYS.get(1.0, END)
            
            subject = self.template_subject
            body = self.template_body
        
            template = self.combobox_box_Template_SYS.get()

        if template.strip() == DEFAULT_COMBO_TEXTBOX: 
            userChoice = messagebox.showwarning("No recipients", "Please select a template and try again.\n\n")
        else: 
            email_recipients = "to: " + recipients + "\n\n" + "cc: " + cc + "\n\n" + "bcc: " + bcc + "\n\n"

            # copy urlstr to clip board
            self.root.clipboard_clear() 
            self.root.clipboard_append(email_recipients)
            self.root.update()

            userChoice = messagebox.showinfo("Copied Recipients to Clipboard", "The following has been copied into your clipboard: CTRL-V away!\n\n" + email_recipients)

    def Display_URL(self): 
        # messagebox.showinfo("URL string", self.urlstr)

        key = self.nb.tab(self.nb.select(), "text")
        if key == 'SYSTEMS': 
            self.generateEmail('SYS') # self.urlstr update
        else: 
            self.generateEmail(key.upper()) # self.urlstr update

        fname = 'link.html'
        with open(fname, 'w+') as f_out:
           make_list = '<li><a href="{}">Click To Send Create Mail</a></li>'.format(self.urlstr)
           f_out.write('{}\n'.format(make_list))

        os.startfile(fname)

    def Launch_TemplateEditor(self):
        
        if os.name == 'nt': 
            subprocess.Popen(['TemplateEditor.pyw'])
        elif os.name == 'posix': 
            subprocess.Popen(['python3', 'TemplateEditor.py'])        
        
        
    def MenuBar_Manage_EmailGroup(self):
        MailtoManage() 
        
        if os.name == 'nt': 
            subprocess.Popen(['py MailtoManage.py'])
        elif os.name == 'posix': 
            subprocess.Popen(['python3', 'MailtoManage.py'])        

    def Backup_EmailFile(self):
    
        # backup email groups
        if (os.path.isfile(self.filename)): 
            with open(self.filename, 'r') as json_file:
                data = json.load(json_file)
                unix_timestamp = datetime.now().timestamp()
                output_backup_fname = "backup/" + self.filename + "_" + str(unix_timestamp) + "_" + getpass.getuser() +".backup"
                with open(output_backup_fname,'w+') as json_file:
                    json.dump(data, json_file, sort_keys=True, indent=4, separators=(',',':'))
            messagebox.showinfo("Backup Complete", "Backup of " + self.filename + ", has been saved as: " + output_backup_fname)
        else: 
            print(json_filename + " cannot be found. Generating default file...")
            sys.exit(2) # exit out cleanly. 
            
        # backup email lookup table
        if USE_ENCODED_DATA: 
            if (os.path.isfile(self.filename_emaildata_lookup_file)): 
                with open(self.filename_emaildata_lookup_file, 'r') as json_file:
                    data = json.load(json_file)
                    unix_timestamp = datetime.now().timestamp()
                    output_backup_fname = "backup/" +self.filename_emaildata_lookup_file+ "_" + str(unix_timestamp) + "_" + getpass.getuser() +".backup"
                    with open(output_backup_fname,'w+') as json_file:
                        json.dump(data, json_file, sort_keys=True, indent=4, separators=(',',':'))
                messagebox.showinfo("Backup Complete", "Backup of " + self.filename_emaildata_lookup_file + ", has been saved as: " + output_backup_fname)        
            else: 
                print(self.filename_emaildata_lookup_file + " cannot be found.")
                sys.exit(2) 

    # modify such that the json_file is the hashed_email_addresses
    # and this function will correctly map the expected email addresses to form 
    # important to read json file as 'utf-8' encoding
    def ReadJSONfile(self, json_filename):
        data = ''
        if (os.path.isfile(json_filename)): 
            with open(json_filename, 'r', encoding='utf8') as json_file:
                data = json.load(json_file)
        else:
            print(json_filename + " cannot be found. Generating default file...")
            #with open(json_filename, 'w') as json_file:
            #    json.dump(DEFAULT_EMAIL_DATA, json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 
            sys.exit(2) # exit out cleanly. 
        return (data)

    def generateTemplateList(self, keyword):
        template_file_list = os.listdir(self.path_to_templates)
        output_file_list = list()
        for item in template_file_list:
            if item.startswith(keyword):
                output_file_list.append(item)

        sorted_filelist = list() # need to sort list in this way
        for file in sorted(list(set(output_file_list))): 
            sorted_filelist.append(file)
                
        return sorted_filelist
            
    def readEmailTemplate(self, template_filename):
        template = ''
        print("Template selected is: " + template_filename)
        if (os.path.isfile(os.path.join(self.path_to_templates, template_filename))):
            with open(os.path.join(self.path_to_templates, template_filename),'r') as template_file:
                template = json.load(template_file)
        else:
            print (template_filename + " cannot be found. Exiting")
            #sys.exit(1)
        
        return template

    def getManufacturerAddresses(self, mid):
        contactlist = list()
        # To get manufacturer addresses 
        for item in self.manufacturer_addresses: 
            for k, v in item.items():
                if item[k] == mid:
                    contactlist.append(item['contacts'])
        
        for item in contactlist:
            print(mid + " contacts are: " + str(item))
 
        return contactlist
         
    def generateEmailStr(self, contactlist):
        outputstr = ''
        for item in list(set(contactlist)):
            outputstr += item+";"
        return outputstr

    def generateEmail(self, key):
        cc = ''
        bcc = ''
        recipients = ''
        subject = ''
        body = ''

        if key == "EGM":
            recipients = self.text_TOoutput_EGM.get(1.0, END)
            cc = self.text_CCoutput_EGM.get(1.0, END)
            bcc = self.text_BCCoutput_EGM.get(1.0, END)

            subject = self.template_subject
            body = self.template_body

            template = self.combobox_box_Template_EGM.get()
                
        elif key == "OTHER":
            recipients = self.text_TOoutput_OTHER.get(1.0, END)
            cc = self.text_CCoutput_OTHER.get(1.0, END)
            bcc = self.text_BCCoutput_OTHER.get(1.0, END)
            
            subject = self.template_subject
            body = self.template_body
            
            template = self.combobox_box_Template_OTHER.get()

        elif key == "SYS":
            recipients = self.text_TOoutput_SYS.get(1.0, END)
            cc = self.text_CCoutput_SYS.get(1.0, END)
            bcc = self.text_BCCoutput_SYS.get(1.0, END)
            
            subject = self.template_subject
            body = self.template_body

            template = self.combobox_box_Template_SYS.get()

        if template.strip() == DEFAULT_COMBO_TEXTBOX: 
            userChoice = messagebox.showwarning("No recipients", "Please select a template and try again.\n\n")
        else:         
            # urllib.parse.quote(subject), urllib.parse.quote(body)))
            urlstr = ''
            if len(cc) == 0:
                if len(bcc) == 0:
                    urlstr = "mailto:%s?subject=%s&body=%s" % (quote(recipients), quote(subject), quote(body))
                else:
                    urlstr = "mailto:%s?bcc=%s&subject=%s&body=%s" % (quote(recipients), quote(bcc), quote(subject), quote(body))
            else: 
                if len(bcc) == 0:
                    urlstr = "mailto:%s?cc=%s&subject=%s&body=%s" % (quote(recipients), quote(cc), quote(subject), quote(body))
                else:
                    urlstr = "mailto:%s?cc=%s&bcc=%s&subject=%s&body=%s" % (quote(recipients), quote(cc), quote(bcc), quote(subject), quote(body))

            if self.validateMailToStrLength(urlstr):
                webbrowser.open(urlstr)

            self.urlstr = urlstr

    def validateMailToStrLength(self, arg):
        userChoice = bool
        if os.name == 'nt': 
            self.CHAR_LIMIT = 2083 # https://support.microsoft.com/en-us/kb/208427
            if len(arg) > self.CHAR_LIMIT:
                userChoice = messagebox.askokcancel("Warning! Email Addresses will get truncated.", "Microsoft URL Length limit reached.\n\nThe HTML mailto: string, currently has: "
                                                + str(len(arg)) + " characters, this exceeds the Maximum of "
                                                + str(self.CHAR_LIMIT) + " characters. \n\nRefer: https://support.microsoft.com/en-us/kb/208427\n\nDo you wish to continue?")
            if userChoice:
                return True
            else:
                return False
        else:
            return True
    
    def uniqueAddresses(self, AllAddressString):
        all_addresses = []
        outstr = ''
        for addresses in AllAddressString.split(";"):
            all_addresses.append(addresses.strip())
            unique_addresses = list(set(all_addresses))
        
        unique_addresses = filter(None, unique_addresses) # remove empty strings
        
        for item in unique_addresses:
            if item != "":  #ignore blanks
                outstr += item+";"
                 
        return outstr

    def generateEmailStr_from_Group(self, email_group):
        data = self.ReadJSONfile(self.filename)
        outstr = ""
        try:       
            for item in data[email_group]: 
                if USE_ENCODED_DATA:
                    item = self.email_lookup_table[item] # translate email hash to email address
                outstr += item+";"
        except: 
            e = sys.exc_info()[0]
            print("WARNING! Index Error while retrieving email addresses from Email Group:'" + str(email_group) + "'. Please check your template for correct Email Groups.")

        return outstr

    def applyTemplate(self, json_data, mode):
        template_to = json_data['Email Template']['to']
        template_cc = json_data['Email Template']['cc']
        template_bcc = json_data['Email Template']['bcc']

        if mode == "OTHER":
            mytextbox_list = [self.text_TOoutput_OTHER, self.text_CCoutput_OTHER, self.text_BCCoutput_OTHER]
        elif mode == "SYS":
            mytextbox_list = [self.text_TOoutput_SYS, self.text_CCoutput_SYS, self.text_BCCoutput_SYS]
        elif mode == "EGM":
            mytextbox_list = [self.text_TOoutput_EGM, self.text_CCoutput_EGM, self.text_BCCoutput_EGM]

        address_list = [template_to, template_cc, template_bcc] # same
                      
        # SUBJECT & BODY
        self.template_subject = json_data['Email Template']['subject']
        self.template_body = json_data['Email Template']['body']
        
        # apply To/CC/BCC Details 
        for i in range(0, len(address_list)): 
            for email_group in address_list[i]:
                mytextbox_list[i].insert(END,self.generateEmailStr_from_Group(email_group))
                
                try:
                    index = self.email_groups_list.index(email_group)
                    if mode == "SYS": 
                        self.vars[index].set(1)
                    elif mode == "EGM":
                        self.vars_egm[index].set(1)   
                except:  # handle the index error exception nicely
                    e = sys.exc_info()[0]
                    print("WARNING! Index Error while trying to set cc: Checkbox options for: '" + str(email_group) + "'. Try selecting 'All' for cc: Options or Check your template for correct Email Groups")

            # Remove Duplicates for all TextBoxes. 
            duplicates_string = mytextbox_list[i].get(1.0, END)
            mytextbox_list[i].delete(1.0, END) 
            mytextbox_list[i].insert(1.0,self.uniqueAddresses(duplicates_string))
    
    def lastModifiedDate(self, fname): 
        lastmodified= os.stat(fname).st_mtime

        # 2017-06-03 02:17:48.263740        
        return datetime.fromtimestamp(lastmodified) 

    ############# GUI Related ################## 
    def setupEGM_Page(self):
        self.root.wm_title("mailto v" + VERSION + " - " + self.filename + " - Last Modified Date: " + str(self.lastModifiedDate(self.filename)))
        
        self.root.resizable(1,1)    
        self.root.focus_force()  
        self.page1 = ttk.Frame(self.nb)
        self.page2 = ttk.Frame(self.nb)
        self.page3 = ttk.Frame(self.nb)

        main_top_frame = ttk.Frame(self.page1)
        main_top_frame.pack(side=TOP, fill=X, expand = False)
        
        ############# TOP FRAME:        
        frame_Header = ttk.Labelframe(main_top_frame, text ='Quick HOWTO:\n\nEither use a template by: "1. Select a Template", then press "2. Generate Email..."')
        frame_Header.pack(side = LEFT, padx = 5, pady=5, fill=X, expand =True)

        # Combo Box for Template
        self.cbTemplate = StringVar()
        self.combobox_box_Template_EGM = ttk.Combobox(frame_Header, justify=LEFT, textvariable=self.cbTemplate, width = 60, state='normal')
        self.combobox_box_Template_EGM.grid(row = 0, column=0, sticky = N, pady=5, padx=5)
        self.combobox_box_Template_EGM.set(DEFAULT_COMBO_TEXTBOX)
        self.combobox_box_Template_EGM['values'] =  self.generateTemplateList("EGM") # generate values based on Template List
        self.combobox_box_Template_EGM.bind('<<ComboboxSelected>>', self.handleComboBoxChanges_EGM)

        # Generate Email Button
        button_generate_email = ttk.Button(frame_Header, text = "2. Generate Email...", command = lambda: self.handleButtonPress('__gen_email_egm__'), width = 20)
        button_generate_email.grid(row = 0, column=1, sticky = N, pady=5, padx=5)

        # Refresh Email Templates List Button
        button_refresh_templates_email = ttk.Button(frame_Header, text = "Refresh Template List", command = lambda: self.handleButtonPress('__refresh_email_list_egm__'), width = 20)
        button_refresh_templates_email.grid(row = 0, column=2, sticky = N, pady=5, padx=5)
        
        self.frame_Address = ttk.Frame(self.page1)
        self.frame_Address.pack(side=TOP, fill=BOTH, expand = True, padx = 5, pady=5)
        self.frame_Address.config(relief = RIDGE, borderwidth = 0)
        
        frame_AddressTextArea = ttk.Frame(self.frame_Address)
        frame_AddressTextArea.pack(side=LEFT, fill=BOTH, expand = True, padx = 5, pady=5)
        frame_AddressTextArea.config(relief = FLAT, borderwidth = 0)
        
        # Text Area for TO: Addresses
        frame_TOtextarea_EGM = ttk.Labelframe(frame_AddressTextArea, text="To Details:")
        frame_TOtextarea_EGM.config(relief = RIDGE, borderwidth = 1)
        frame_TOtextarea_EGM.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        # Text Area for CC: Options
        self.frame_CCframe_EGM = ScrollableFrame(self.frame_Address) # Scrollable Frames here. 
        self.frame_CCframe_EGM.config(relief = RIDGE, borderwidth = 1)
        self.frame_CCframe_EGM.pack(fill=Y, side=BOTTOM, expand = True)

        self.text_TOoutput_EGM = Text(frame_TOtextarea_EGM, height=1, width=40)
        S = Scrollbar(frame_TOtextarea_EGM, command=self.text_TOoutput_EGM.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_TOoutput_EGM.configure(yscrollcommand=S.set)
        self.text_TOoutput_EGM.pack(side=LEFT, fill=BOTH, expand=True)
         
        # Text Area for CC: Addresses
        frame_CCtextarea_EGM = ttk.Labelframe(frame_AddressTextArea, text="cc Details:")
        frame_CCtextarea_EGM.config(relief = RIDGE, borderwidth = 1)
        frame_CCtextarea_EGM.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        self.text_CCoutput_EGM = Text(frame_CCtextarea_EGM, height = 1, width=40)
        S = Scrollbar(frame_CCtextarea_EGM, command=self.text_CCoutput_EGM.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_CCoutput_EGM.configure(yscrollcommand=S.set)
        self.text_CCoutput_EGM.pack(side=LEFT, fill=BOTH, expand=True)
        
        # Text Area for BCC: Addresses
        frame_BCCtextarea_EGM = ttk.Labelframe(frame_AddressTextArea, text="bcc Details:")
        frame_BCCtextarea_EGM.config(relief = RIDGE, borderwidth = 1)
        frame_BCCtextarea_EGM.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        self.text_BCCoutput_EGM = Text(frame_BCCtextarea_EGM, height=1, width=40)
        S = Scrollbar(frame_BCCtextarea_EGM, command=self.text_BCCoutput_EGM.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_BCCoutput_EGM.configure(yscrollcommand=S.set)
        self.text_BCCoutput_EGM.pack(side=LEFT, fill=BOTH, expand=True)  
        
        # CC Radiobutton modes
        MODES = [
            ("EGM only", "1"),
            ("All","2"),
        ]
        
        self.vars_rb_mode = IntVar()
        self.vars_rb_mode.set(1)
        for text, mode in MODES:
            b = ttk.Radiobutton(self.page1, text=text, variable=self.vars_rb_mode, value=mode, command=self.HandleRadioButton_EGM)
            b.pack(side = RIGHT, anchor="e")
        Label(self.page1, text="Select Filter: ").pack(side = RIGHT, anchor="e")
        
        ## cc: Options
        self.generateEmailGroups("EGM")

        ttk.Label(self.frame_Address, text="Email Groups: Refer INET for Details.", foreground="red", font=("Arial", 14)).pack(side=TOP, anchor='s', fill =Y, expand = False, pady=5, padx=5)
        self.DrawCCCheckButtons_EGM() # Checkboxes
        
        #frame_Header
        frame_buttons = ttk.Labelframe(main_top_frame, text='\n\nOr Select "Email Groups" to populate the to:, cc: and bcc: Email fields:')
        frame_buttons.pack(side = RIGHT, expand = False, fill=Y, padx=5, pady=5)
        
        # Apply To: Button
        button_EGM_Apply = ttk.Button(frame_buttons, text = "Apply To:", command = lambda: self.handleButtonPress('__button_to_apply_egm__'), width=20)
        button_EGM_Apply.grid(row = 0, column=0, sticky = 'n')
        
        # Apply CC Button
        button_EGM_Apply = ttk.Button(frame_buttons, text = "Apply cc:", command = lambda: self.handleButtonPress('__button_cc_apply_egm__'), width=20)
        button_EGM_Apply.grid(row = 0, column=1, sticky = 'n')

        # Apply BCC Button
        button_EGM_Apply = ttk.Button(frame_buttons, text = "Apply bcc:", command = lambda: self.handleButtonPress('__button_bcc_apply_egm__'), width=20)
        button_EGM_Apply.grid(row = 0, column=2, sticky = 'n')

        # Clear To: Button
        button_EGM_clear = ttk.Button(frame_buttons, text = "Clear To:", command = lambda: self.handleButtonPress('__button_to_clear_egm__'), width=20)
        button_EGM_clear.grid(row = 1, column=0, sticky = 'n')
        
        # Clear CC Button
        button_EGM_clear = ttk.Button(frame_buttons, text = "Clear cc:", command = lambda: self.handleButtonPress('__button_cc_clear_egm__'), width=20)
        button_EGM_clear.grid(row = 1, column=1, sticky = 'n')

        # Clear BCC Button
        button_EGM_clear = ttk.Button(frame_buttons, text = "Clear bcc:", command = lambda: self.handleButtonPress('__button_bcc_clear_egm__'), width=20)
        button_EGM_clear.grid(row = 1, column=2, sticky = 'n')
        
        ################ Bottom FRAME ##############
        frame_bottombuttons = ttk.Frame(self.page1)
        frame_bottombuttons.pack(side=BOTTOM, fill=X, expand = False,)
        frame_bottombuttons.config(relief = FLAT, borderwidth = 0)    
           
         # Button To Clear To: Details
        button_clearform_EGM= ttk.Button(frame_bottombuttons, text = "Clear Form", width = 20,command = lambda: self.handleButtonPress('__clear_form_egm__'))                                             
        button_clearform_EGM.grid(row=0, column=1,  sticky='s',  padx=5, pady=5)

        self.nb.add(self.page1, text="EGM")
        self.nb.add(self.page2, text="Systems")
        self.nb.add(self.page3, text="Other")
        self.nb.pack(expand=1, fill="both")
        
    def setupSystems_Page(self):
        main_top_frame = ttk.Frame(self.page2)
        main_top_frame.pack(side=TOP, fill=X, expand = False)

        frame_Header = ttk.Labelframe(main_top_frame, text ='1. Select a "Template"; 2. Press "Generate Email..."')
        frame_Header.pack(side = LEFT, padx = 5, pady=5, fill=X, expand = False)

        ############# TOP FRAME: 
        # Combo Box for Template
        self.cbTemplate_SYS = StringVar()
        self.combobox_box_Template_SYS = ttk.Combobox(frame_Header, justify=LEFT, textvariable=self.cbTemplate_SYS, width = 60, state='readonly')
        self.combobox_box_Template_SYS.pack(side = LEFT, fill=X, padx=5, pady=5)
        self.combobox_box_Template_SYS.set(DEFAULT_COMBO_TEXTBOX)
        self.combobox_box_Template_SYS['values'] =  self.generateTemplateList("SYS") # generate values based on Template List
        self.combobox_box_Template_SYS.bind('<<ComboboxSelected>>', self.handleComboBoxChanges_SYS)

        # Generate Email Button
        button_start = ttk.Button(frame_Header, text = "2. Generate Email...", command = lambda: self.handleButtonPress('__gen_email_sys__'), width = 20)
        button_start.pack(side=LEFT, padx=5,pady=5)
        
        # Refresh Email Templates List Button
        button_refresh_templates_email = ttk.Button(frame_Header, text = "Refresh Template List", command = lambda: self.handleButtonPress('__refresh_email_list_sys__'), width = 20)
        button_refresh_templates_email.pack(side=LEFT, padx=5,pady=5)
        
        self.frame_Address_SYS = ttk.Frame(self.page2)
        self.frame_Address_SYS.pack(side=TOP, fill=BOTH, expand = True, padx = 5, pady=5)
        self.frame_Address_SYS.config(relief = RIDGE, borderwidth = 0)
        
        frame_AddressTextArea = ttk.Frame(self.frame_Address_SYS)
        frame_AddressTextArea.pack(side=LEFT, fill=BOTH, expand = True, padx = 5, pady=5)
        frame_AddressTextArea.config(relief = FLAT, borderwidth = 0)
        
        # Text Area for TO: Addresses
        frame_TOtextarea_SYS = ttk.Labelframe(frame_AddressTextArea, text="To: Details:")
        frame_TOtextarea_SYS.config(relief = RIDGE, borderwidth = 1)
        frame_TOtextarea_SYS.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        # Text Area for CC: Options
        self.frame_CCframe_SYS = ScrollableFrame(self.frame_Address_SYS)
        self.frame_CCframe_SYS.config(relief = RIDGE, borderwidth = 1)
        self.frame_CCframe_SYS.pack(fill=Y, side=BOTTOM, expand = True)

        self.text_TOoutput_SYS = Text(frame_TOtextarea_SYS, height=1, width=40)
        S = Scrollbar(frame_TOtextarea_SYS, command=self.text_TOoutput_SYS.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_TOoutput_SYS.configure(yscrollcommand=S.set)
        self.text_TOoutput_SYS.pack(side=LEFT, fill=BOTH, expand=True)
         
        # Text Area for CC: Addresses
        frame_CCtextarea_SYS = ttk.Labelframe(frame_AddressTextArea, text="cc: Details:")
        frame_CCtextarea_SYS.config(relief = RIDGE, borderwidth = 1)
        frame_CCtextarea_SYS.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        self.text_CCoutput_SYS = Text(frame_CCtextarea_SYS, height = 1, width=40)
        S = Scrollbar(frame_CCtextarea_SYS, command=self.text_CCoutput_SYS.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_CCoutput_SYS.configure(yscrollcommand=S.set)
        self.text_CCoutput_SYS.pack(side=LEFT, fill=BOTH, expand=True)

        # Text Area for BCC: Addresses
        frame_BCCtextarea_SYS = ttk.Labelframe(frame_AddressTextArea, text="bcc: Details:")
        frame_BCCtextarea_SYS.config(relief = RIDGE, borderwidth = 1)
        frame_BCCtextarea_SYS.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        self.text_BCCoutput_SYS = Text(frame_BCCtextarea_SYS, height=1, width=40)
        S = Scrollbar(frame_BCCtextarea_SYS, command=self.text_BCCoutput_SYS.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_BCCoutput_SYS.configure(yscrollcommand=S.set)
        self.text_BCCoutput_SYS.pack(side=LEFT, fill=BOTH, expand=True)          
       
        # Radio Button modes
        MODES = [
            ("Systems only", "1"),
            ("All","2"),
        ]
        self.vars_rb_mode_sys = IntVar()
        self.vars_rb_mode_sys.set(1)
    
        for text, mode in MODES:
            b = ttk.Radiobutton(self.page2, text=text, variable=self.vars_rb_mode_sys, value=mode, command=self.HandleRadioButton_SYS)
            b.pack(side = RIGHT, anchor="e")
        
        Label(self.page2, text="Select Filter: ").pack(side = RIGHT, anchor="e")
    
        ## cc: Options
        self.generateEmailGroups("SYS")

        ttk.Label(self.frame_Address_SYS, text="Email Groups: Refer FM14 for Details.", font=("Arial", 18), foreground="red").pack(side=TOP, anchor='s', fill =Y, expand = False, pady=5, padx=5)
        self.DrawCCCheckButtons_SYS()
       
        #frame_Header
        frame_buttons = ttk.Labelframe(main_top_frame, text="or Select Email Groups to specific email Fields:")
        frame_buttons.pack(side = RIGHT, expand = False, fill=Y, padx=5, pady=5)

        # Apply To: Button
        button_To_SYS_Apply = ttk.Button(frame_buttons, text = "Apply To:", command = lambda: self.handleButtonPress('__button_to_apply_sys__'), width=20)
        button_To_SYS_Apply.grid(row = 0, column=0, sticky = 'n')
        
        # Apply CC Button
        button_CC_SYS_Apply = ttk.Button(frame_buttons, text = "Apply CC:", command = lambda: self.handleButtonPress('__button_cc_apply_sys__'), width = 20)
        button_CC_SYS_Apply.grid(row = 0, column=1, sticky = 'n')
        
        # Apply BCC Button
        button_BCC_SYS_Apply = ttk.Button(frame_buttons, text = "Apply bcc:", command = lambda: self.handleButtonPress('__button_bcc_apply_sys__'), width=20)
        button_BCC_SYS_Apply.grid(row = 0, column=2, sticky = 'n')
        
        # Clear To: Button
        button_To_SYS_clear = ttk.Button(frame_buttons, text = "Clear To:", command = lambda: self.handleButtonPress('__button_to_clear_sys__'), width=20)
        button_To_SYS_clear.grid(row = 1, column=0, sticky = 'n')
        
        # Clear CC: Button
        button_CC_SYS_clear = ttk.Button(frame_buttons, text = "Clear cc:", command = lambda: self.handleButtonPress('__button_cc_clear_sys__'), width = 20)
        button_CC_SYS_clear.grid(row = 1, column=1, sticky = 'n')
     
        # Clear BCC Button
        button_BCC_SYS_clear = ttk.Button(frame_buttons, text = "Clear bcc:", command = lambda: self.handleButtonPress('__button_bcc_clear_sys__'), width=20)
        button_BCC_SYS_clear.grid(row = 1, column=2, sticky = 'n')
        
        ################ Bottom FRAME ##############
        frame_bottombuttons = ttk.Frame(self.page2)
        frame_bottombuttons.pack(side=BOTTOM, fill=X, expand = False)
        frame_bottombuttons.config(relief = FLAT, borderwidth = 0)       
         # Button To Clear To: Details
        button_ADD_contacts= ttk.Button(frame_bottombuttons, text = "Clear Form", width = 20,command = lambda: self.handleButtonPress('__clear_form_sys__'))                                             
        button_ADD_contacts.grid(row=0, column=1,  sticky='s',  padx=5, pady=5)
    
    def setupOther_Page(self):
        frame_Header = ttk.Labelframe(self.page3, text ='Quick HOWTO using Templates:\n1. Select a "Template"; 2. Make Modifications if need be; 3."Generate Email"')
        frame_Header.pack(side = TOP, padx = 5, pady=5, fill=BOTH, expand = False)

        ############# TOP FRAME: 
        # Combo Box for Template
        self.cbTemplate_OTHER = StringVar()
        self.combobox_box_Template_OTHER = ttk.Combobox(frame_Header, justify=LEFT, textvariable=self.cbTemplate_OTHER, width = 40, state='readonly')
        self.combobox_box_Template_OTHER.pack(side = LEFT, fill=X, padx=5, pady=5)
        self.combobox_box_Template_OTHER.set(DEFAULT_COMBO_TEXTBOX)
        self.combobox_box_Template_OTHER['values'] =  self.generateTemplateList("OTHER") # generate values based on Template List
        self.combobox_box_Template_OTHER.bind('<<ComboboxSelected>>', self.handleComboBoxChanges_OTHER)

        # Generate Email Button
        button_start = ttk.Button(frame_Header, text = "2. Generate Email...", command = lambda: self.handleButtonPress('__gen_email_other__'), width = 20)
        button_start.pack(side=LEFT, padx=5,pady=5)

        # Refresh Email Templates List Button
        button_refresh_templates_email = ttk.Button(frame_Header, text = "Refresh Template List", command = lambda: self.handleButtonPress('__refresh_email_list_other__'), width = 20)
        button_refresh_templates_email.pack(side=LEFT, padx=5,pady=5)
        
        frame_AddressTextArea = ttk.Frame(self.page3)
        frame_AddressTextArea.pack(side=TOP, fill=BOTH, expand = True, padx = 5, pady=5)
        frame_AddressTextArea.config(relief = FLAT, borderwidth = 0)
        
        # Text Area for TO: Addresses
        frame_TOtextarea_OTHER = ttk.Labelframe(frame_AddressTextArea, text="To Details:")
        frame_TOtextarea_OTHER.config(relief = RIDGE, borderwidth = 1)
        frame_TOtextarea_OTHER.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        #frame_TOtextarea_OTHER.grid(row=1, columnspan=4, sticky='w',padx=5,pady=5)
        
        self.text_TOoutput_OTHER = Text(frame_TOtextarea_OTHER, height=10, width=50)
        S = Scrollbar(frame_TOtextarea_OTHER, command=self.text_TOoutput_OTHER.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_TOoutput_OTHER.configure(yscrollcommand=S.set)
        self.text_TOoutput_OTHER.pack(side=LEFT, fill=BOTH, expand=True)
         
        # Text Area for CC: Addresses
        frame_CCtextarea_OTHER = ttk.Labelframe(frame_AddressTextArea, text="cc Details:")
        frame_CCtextarea_OTHER.config(relief = RIDGE, borderwidth = 1)
        frame_CCtextarea_OTHER.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        #frame_TOtextarea_OTHER.grid(row=1, columnspan=4, sticky='w',padx=5,pady=5)
        
        self.text_CCoutput_OTHER = Text(frame_CCtextarea_OTHER, height=10, width=50)
        S = Scrollbar(frame_CCtextarea_OTHER, command=self.text_CCoutput_OTHER.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_CCoutput_OTHER.configure(yscrollcommand=S.set)
        self.text_CCoutput_OTHER.pack(side=LEFT, fill=BOTH, expand=True)

        # Text Area for BCC: Addresses
        frame_BCCtextarea_OTHER = ttk.Labelframe(frame_AddressTextArea, text="bcc Details:")
        frame_BCCtextarea_OTHER.config(relief = RIDGE, borderwidth = 1)
        frame_BCCtextarea_OTHER.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        #frame_TOtextarea_OTHER.grid(row=1, columnspan=4, sticky='w',padx=5,pady=5)
        
        self.text_BCCoutput_OTHER = Text(frame_BCCtextarea_OTHER, height=10, width=50)
        S = Scrollbar(frame_BCCtextarea_OTHER, command=self.text_BCCoutput_OTHER.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_BCCoutput_OTHER.configure(yscrollcommand=S.set)
        self.text_BCCoutput_OTHER.pack(side=LEFT, fill=BOTH, expand=True)
                
        ################ Bottom FRAME ##############
        frame_bottombuttons = ttk.Frame(self.page3)
        frame_bottombuttons.pack(side=BOTTOM, fill=X, expand = False)
        frame_bottombuttons.config(relief = FLAT, borderwidth = 0)       
         # Button To Clear To: Details
        button_ADD_contacts= ttk.Button(frame_bottombuttons, text = "Clear Form", width = 20,command = lambda: self.handleButtonPress('__clear_form_other__'))                                             
        button_ADD_contacts.grid(row=0, column=1,  sticky='s',  padx=5, pady=5)

    def DrawCCCheckButtons_EGM (self): 
        self.vars_egm = []
        ## cc: checkboxes
        for i in range(len(self.email_groups_list)):
            var = IntVar()
            ttk.Checkbutton(self.frame_CCframe_EGM.interior, text=str(self.email_groups_list[i]), variable =var, onvalue=1, offvalue=0).pack(side=TOP, anchor='w', expand=True)
            self.vars_egm.append(var)

    def DrawCCCheckButtons_SYS(self): 
        self.vars = []
        ## cc: checkboxes
        for i in range(len(self.email_groups_list)):
            var = IntVar()
            Checkbutton(self.frame_CCframe_SYS.interior, text=str(self.email_groups_list[i]), variable =var, onvalue=1, offvalue=0).pack(side=TOP, anchor='w', expand=True)
            self.vars.append(var)
           
    ############ EVENT handling ################
    def HandleRadioButton_SYS(self): 
        self.frame_CCframe_SYS.destroy()
        self.generateEmailGroups("SYS")
        self.frame_CCframe_SYS = ScrollableFrame(self.frame_Address_SYS)
        self.frame_CCframe_SYS.config(relief = RIDGE, borderwidth = 1)
        self.frame_CCframe_SYS.pack(side = RIGHT, fill=Y, expand = False)
        self.DrawCCCheckButtons_SYS()
        
    
    def HandleRadioButton_EGM(self):
        # 1 clear the canvas. 
        self.frame_CCframe_EGM.destroy()
        self.generateEmailGroups("EGM")
        self.frame_CCframe_EGM = ScrollableFrame(self.frame_Address)
        self.frame_CCframe_EGM.config(relief = RIDGE, borderwidth = 1)
        self.frame_CCframe_EGM.pack(side = RIGHT, fill=Y, expand = False)
        self.DrawCCCheckButtons_EGM()
               

    def handleButtonPress(self, event):
        if event == '__button_cc_apply_sys__': 
            self.generateEmailGroups("SYS")
            self.text_CCoutput_SYS.delete(1.0, END) # Clear the field
            for i in range(len(self.vars)):
                if (self.vars[i].get() == 1):
                    self.text_CCoutput_SYS.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i]))
        
        elif event == '__button_to_apply_sys__':
            self.generateEmailGroups("SYS")
            self.text_TOoutput_SYS.delete(1.0, END) # clear
            for i in range(len(self.vars)):
                if (self.vars[i].get() == 1):
                    self.text_TOoutput_SYS.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i])) 
        
        elif event == '__button_bcc_apply_sys__':
            self.generateEmailGroups("SYS")
            self.text_BCCoutput_SYS.delete(1.0, END) # clear
            for i in range(len(self.vars)):
                if (self.vars[i].get() == 1):
                    self.text_BCCoutput_SYS.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i]))   
                                     
        elif event == '__button_cc_apply_egm__':
            self.cc_address_list = list()
            self.generateEmailGroups("EGM")
            self.text_CCoutput_EGM.delete(1.0, END) # Clear the field
            for i in range(len(self.vars_egm)):
                if (self.vars_egm[i].get() == 1):
                    self.text_CCoutput_EGM.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i]))
                    self.cc_address_list.append(self.email_groups_list[i])
             
        elif event == '__button_to_apply_egm__':
            self.to_address_list = list()
            self.generateEmailGroups("EGM")

            self.text_TOoutput_EGM.delete(1.0, END) # clear
            for i in range(len(self.vars_egm)):
                if (self.vars_egm[i].get() == 1):
                    self.text_TOoutput_EGM.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i])) 
                    # Save Keys related to self.vars_egm
                    self.to_address_list.append(self.email_groups_list[i])

        elif event == '__button_bcc_apply_egm__':
            self.bcc_address_list = list()
            self.generateEmailGroups("EGM")
            
            self.text_BCCoutput_EGM.delete(1.0, END) # clear
            for i in range(len(self.vars_egm)):
                if (self.vars_egm[i].get() == 1):
                    self.text_BCCoutput_EGM.insert(END,self.generateEmailStr_from_Group(self.email_groups_list[i])) 
                    self.bcc_address_list.append(self.email_groups_list[i])
        
        elif event == '__button_cc_clear_sys__':
            for i in range(len(self.vars)):
                self.vars[i].set(0)
            self.text_CCoutput_SYS.delete(1.0, END) 
        elif event == '__button_to_clear_sys__':
            for i in range(len(self.vars)):
                self.vars[i].set(0)
            self.text_TOoutput_SYS.delete(1.0, END) 
        elif event == '__button_bcc_clear_sys__':
            for i in range(len(self.vars)):
                self.vars[i].set(0)
            self.text_BCCoutput_SYS.delete(1.0, END) 
        elif event == '__button_cc_clear_egm__':
            for i in range(len(self.vars_egm)):
                self.vars_egm[i].set(0)
            self.text_CCoutput_EGM.delete(1.0, END) 
        elif event == '__button_to_clear_egm__':
            for i in range(len(self.vars_egm)):
                self.vars_egm[i].set(0)
            self.text_TOoutput_EGM.delete(1.0, END)
        elif event == '__button_bcc_clear_egm__':
            for i in range(len(self.vars_egm)):
                self.vars_egm[i].set(0)
            self.text_BCCoutput_EGM.delete(1.0, END)         
        elif event == '__clear_form_sys__':
            self.text_TOoutput_SYS.delete(1.0, END) 
            self.text_CCoutput_SYS.delete(1.0, END) 
            self.text_BCCoutput_SYS.delete(1.0, END)
            self.combobox_box_Template_SYS.set("1. Select a Template...")       
            self.handleButtonPress("__button_cc_clear_sys__")
            self.template_subject = DEFAULT_SUBJECT
            self.template_body = DEFAULT_BODY
            self.HandleRadioButton_SYS()
        elif event == '__clear_form_egm__':
            self.text_TOoutput_EGM.delete(1.0, END) 
            self.text_CCoutput_EGM.delete(1.0, END) 
            self.text_BCCoutput_EGM.delete(1.0, END) 
            self.combobox_box_Template_EGM.set("1. Select a Template...")       
            self.handleButtonPress("__button_cc_clear_egm__")
            self.template_subject = DEFAULT_SUBJECT
            self.template_body = DEFAULT_BODY
            self.HandleRadioButton_EGM()
        elif event == '__clear_form_other__':
            self.text_TOoutput_OTHER.delete(1.0, END)
            self.text_CCoutput_OTHER.delete(1.0,END)
            self.text_BCCoutput_OTHER.delete(1.0,END)
            self.combobox_box_Template_OTHER.set("1. Select a Template...")       
        elif event == '__gen_email_other__':
            self.generateEmail("OTHER")
        elif event == '__gen_email_sys__':
            self.generateEmail("SYS")
        elif event == '__gen_email_egm__':
            self.generateEmail("EGM")
        elif event == '__refresh_email_list_egm__':
            self.combobox_box_Template_EGM['values'] =  self.generateTemplateList("EGM") 
        elif event == '__refresh_email_list_sys__':
            self.combobox_box_Template_SYS['values'] =  self.generateTemplateList("SYS") 
        elif event == '__refresh_email_list_other__':
            self.combobox_box_Template_OTHER['values'] =  self.generateTemplateList("OTHER") 
        elif event == '__save_template_egm__':
            self.saveTemplate(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, "EGM")

    def handleComboBoxChanges_SYS(self, event):
        self.text_TOoutput_SYS.delete(1.0, END)
        self.text_CCoutput_SYS.delete(1.0, END)
        self.text_BCCoutput_SYS.delete(1.0, END)  
        self.handleButtonPress("__button_cc_clear_sys__")

        template = ''
        template_json_data = ''
        _templateChoice = self.combobox_box_Template_SYS.get()
        if _templateChoice in self.generateTemplateList("SYS"):
            template_json_data = self.readEmailTemplate(_templateChoice) # Read Template Data and return the JSON data object
        else:
            print("could not read file: " + _templateChoice)
        
        self.generateEmailGroups("SYS")
        self.applyTemplate(template_json_data, "SYS")
        
    def handleComboBoxChanges_OTHER(self, event):
        self.text_TOoutput_OTHER.delete(1.0, END)
        self.text_CCoutput_OTHER.delete(1.0, END)
        self.text_BCCoutput_OTHER.delete(1.0, END)  

        template = ''
        _templateChoice = self.combobox_box_Template_OTHER.get()
        if _templateChoice in self.generateTemplateList("OTHER"):
            template_json_data = self.readEmailTemplate(_templateChoice) # Read Template Data and return the JSON data object
        else:
            print("could not read file: " + _templateChoice)
         
        self.applyTemplate(template_json_data, "OTHER")

    def handleComboBoxChanges_EGM(self, event):
        self.text_TOoutput_EGM.delete(1.0, END)
        self.text_CCoutput_EGM.delete(1.0, END)
        self.text_BCCoutput_EGM.delete(1.0, END)  
        self.handleButtonPress("__button_cc_clear_egm__")

        template = ''
        template_json_data = ''
        _templateChoice = self.combobox_box_Template_EGM.get()
        if _templateChoice in self.generateTemplateList("EGM"):
            template_json_data = self.readEmailTemplate(_templateChoice) # Read Template Data and return the JSON data object
        else:
            print("could not read file: " + _templateChoice)
        
        self.generateEmailGroups("EGM")
        self.applyTemplate(template_json_data, "EGM")

    def generateEmailGroups(self, mode): 
        self.email_groups_list = list() 
        if mode == "EGM":
            ignore_groups_starting_with = "SYS"
            if self.vars_rb_mode.get() == 1: #  EGM mode 
                # Generate the Email Group List
                for k,v in self.data.items(): # set defaults
                    if str(k).startswith(ignore_groups_starting_with):
                        pass # ignore 
                    else:
                        self.email_groups_list.append(k)
                #self.email_groups_list.sort()
            else: # ALL Filter
                for k,v in self.data.items(): # set defaults
                    self.email_groups_list.append(k)
        
        elif mode == "SYS":
            ignore_groups_starting_with = "EGM"
            if self.vars_rb_mode_sys.get() == 1: #  EGM mode 
                # Generate the Email Group List
                for k,v in self.data.items(): # set defaults
                    if str(k).startswith(ignore_groups_starting_with):
                        pass # ignore 
                    else:
                        self.email_groups_list.append(k)
                #self.email_groups_list.sort()
            else: # ALL Filter
                for k,v in self.data.items(): # set defaults
                    self.email_groups_list.append(k)
            
        else: # All
           # unkonwn mode. 
           print("Error, unexpected mode: " + mode)
           sys.exit(1)       
        
        self.email_groups_list.sort()
    
    
def main():
    app = mailto()

if __name__ == "__main__": main()
