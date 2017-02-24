#!/usr/bin/python3

import json
import os, sys
import tkinter as tk
import getpass

from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime
from urllib.parse import quote

# v0.1 Initial Release

VERSION = "0.1"
DEFAULT_SUBJECT = "[ENTER EMAIL SUBJECT]"
DEFAULT_BODY = "[This is an output email from 'mailto' script!]\n\n\n"

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

class TemplateEditor:

    # Constructor
    def __init__(self):
        self.pathtotemplates = "templates/"
        self.template_subject = DEFAULT_SUBJECT
        self.template_body = DEFAULT_BODY
        self.filename = "emaildata.json"
        self.root = tk.Tk()       
        self.to_address_list = list()
        self.cc_address_list = list()
        self.bcc_address_list = list()
        
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        optionmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.root.destroy)
        
        self.root.config(menu=menubar)
        self.data = self.ReadJSONfile(self.filename)  
        self.setupGUI()
        self.root.mainloop()    

    def ReadJSONfile(self, json_filename):
        data = ''
        if (os.path.isfile(json_filename)): 
            with open(json_filename, 'r') as json_file:
                data = json.load(json_file)
        else:
            print(json_filename + " cannot be found. Generating default file...")
            with open(json_filename, 'w') as json_file:
                json.dump(DEFAULT_EMAIL_DATA, json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 
            sys.exit(2) # exit out cleanly. 
        return (data)

    def generateTemplateList(self):
        template_file_list = os.listdir(self.pathtotemplates)
        output_file_list = list()
        for item in template_file_list:
            output_file_list.append(item)
            
        return output_file_list
            
    def readEmailTemplate(self, template_filename):
        template = ''
        print("Template selected is: " + template_filename)
        if (os.path.isfile(os.path.join(self.pathtotemplates, template_filename))):
            with open(os.path.join(self.pathtotemplates, template_filename),'r') as template_file:
                template = json.load(template_file)
        else:
            print (template_filename + " cannot be found. Exiting")
            #sys.exit(1)
        
        return template

    def saveTemplate(self, to_groups, cc_groups, bcc_groups, body, subject):
        json_data = self.ReadJSONfile(self.filename)
        # remove duplicates. 
        to_groups = list(set(to_groups))
        cc_groups = list(set(cc_groups))
        bcc_groups = list(set(bcc_groups))
        
        SavedTemplate = { "title" : self.combobox_box_Template_EGM.get(),
                          "to" : to_groups,
                          "cc" : cc_groups,
                          "bcc" : bcc_groups,
                          "subject" : subject,
                          "body": body }
        template = { "Email Template": SavedTemplate }
        
        #print(json.dumps(template, indent=4, sort_keys=False, separators=(',',':')))
        with open("templates/" + self.combobox_box_Template_EGM.get() + ".json", 'w') as json_file: 
            json.dump(template, json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 

        messagebox.showinfo("Saved New Template", "Template Name:\n\n" + self.combobox_box_Template_EGM.get() + ".json" + 
            "\n\nto: " + str(to_groups) + 
            "\n\ncc: " + str(cc_groups) + 
            "\n\nbcc:" + str(bcc_groups) + 
            "\n\nsubject: " + str(subject) + 
            "\n\nbody: " + str(body))

    def generateJSONObject_to_Display(self, to_groups, cc_groups, bcc_groups, body, subject):
        # remove duplicates. 
        to_groups = list(set(to_groups))
        cc_groups = list(set(cc_groups))
        bcc_groups = list(set(bcc_groups))

        SavedTemplate = { "title" : self.combobox_box_Template_EGM.get(),
                          "to" : to_groups,
                          "cc" : cc_groups,
                          "bcc" : bcc_groups,
                          "subject" : subject,
                          "body": body }
        template = { "Email Template": SavedTemplate }
        self.text_JSONoutput.delete(1.0, END) 
        self.text_JSONoutput.insert(1.0,json.dumps(template, indent=4, sort_keys=True, separators=(',',':'))) 


    ############# GUI Related ################## 
    def setupGUI(self):
        self.root.wm_title("TemplateEditor v" + VERSION)
        
        self.root.resizable(1,1)    
        self.root.focus_force()  

        main_top_frame = ttk.Frame(self.root)
        main_top_frame.pack(side=TOP, fill=X, expand = False)
        
        helptext = "Quick HOWTO:\n\n1. Use an existing Email Template as a starting point template or populate all fields manually."
        
        ############# TOP FRAME:        
        frame_Header = ttk.Labelframe(main_top_frame, text=helptext)
        frame_Header.pack(side = TOP, padx = 5, pady=5, fill=X, expand =True)

        # Combo Box for Template
        self.cbTemplate = StringVar()
        self.combobox_box_Template_EGM = ttk.Combobox(frame_Header, justify=LEFT, textvariable=self.cbTemplate, width = 60, state='normal')
        #self.combobox_box_Template_EGM.pack(side = LEFT, padx=5, pady=5)
        self.combobox_box_Template_EGM.grid(row = 0, column=0, sticky = N, pady=5, padx=5)
        self.combobox_box_Template_EGM.set('1. Select a Template...')
        self.combobox_box_Template_EGM['values'] =  self.generateTemplateList() # generate values based on Template List
        self.combobox_box_Template_EGM.bind('<<ComboboxSelected>>', self.handleComboBoxChanges)

        # Refresh Email Templates List Button
        button_refresh_templates_email = ttk.Button(frame_Header, text = "Refresh Template List", command = lambda: self.handleButtonPress('__refresh_email_list_egm__'), width = 20)
        button_refresh_templates_email.grid(row = 0, column=2, sticky = N, pady=5, padx=5)
        
        # Save Template
        button_save_template = ttk.Button(frame_Header, text = "Save Template", command = lambda: self.handleButtonPress('__save_template_egm__'), width = 20)
        button_save_template.grid(row = 0, column=1, sticky = N, pady=5, padx=5)       
     
        self.frame_Address = ttk.Frame(self.root)
        self.frame_Address.pack(side=TOP, fill=BOTH, expand = True, padx = 5, pady=5)
        self.frame_Address.config(relief = RIDGE, borderwidth = 0)
        
        frame_AddressTextArea = ttk.Frame(self.frame_Address)
        frame_AddressTextArea.pack(side=LEFT, fill=BOTH, expand = True, padx = 5, pady=5)
        frame_AddressTextArea.config(relief = RIDGE, borderwidth = 0)
        
        # Text Area for TO: Addresses
        frame_TOtextarea_EGM = ttk.Labelframe(frame_AddressTextArea, text="JSON Email Template:")
        frame_TOtextarea_EGM.config(relief = RIDGE, borderwidth = 1)
        frame_TOtextarea_EGM.pack(side = TOP, fill=BOTH, expand = True, padx=5, pady=5,anchor='n')
        
        # Text Area for CC: Options
        self.frame_JSON_View = ScrollableFrame(self.frame_Address) # Scrollable Frames here. 
        self.frame_JSON_View.config(relief = RIDGE, borderwidth = 1)
        self.frame_JSON_View.pack(fill=Y, side=BOTTOM, expand = True)

        self.text_JSONoutput = Text(frame_TOtextarea_EGM, height=1, width=40)
        S = Scrollbar(frame_TOtextarea_EGM, command=self.text_JSONoutput.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_JSONoutput.configure(yscrollcommand=S.set)
        self.text_JSONoutput.pack(side=LEFT, fill=BOTH, expand=True)
        

        # CC Radiobutton modes
        MODES = [
            ("EGM only", "1"),
            ("SYS only", "2"),
            ("All","3"),
        ]
        
        self.vars_editor_rb_mode_editor = IntVar()
        self.vars_editor_rb_mode_editor.set(3)
        for text, mode in MODES:
            b = ttk.Radiobutton(self.root, text=text, variable=self.vars_editor_rb_mode_editor, value=mode, command=self.HandleRadioButton)
            b.pack(side = RIGHT, anchor="e")
        Label(self.root, text="Select Filter: ").pack(side = RIGHT, anchor="e")
        
        ## cc: Options
        #self.refresh_email_groups_list_editor_EGM()
        self.generateEmailGroupsEditor()

        ttk.Label(self.frame_Address, text="Email Groups: Refer FM14 for Details.", foreground="red").pack(side=TOP, anchor='s', fill =Y, expand = False, pady=5, padx=5)
        self.DrawCheckButtons() # Checkboxes
        
        #frame_Header
        frame_buttons = ttk.Labelframe(main_top_frame, text='Select "Email Groups" to populate the to:, cc: and bcc: Email fields:')
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
        
        frame_subject = ttk.Frame(main_top_frame)
        frame_subject.pack(side = TOP, expand = False, fill = BOTH, padx=5, pady=5)
        
        lblSubject = ttk.Label(frame_subject, text="Subject: ")
        lblSubject.pack(side = LEFT, expand = False, fill = X, padx=5, pady=5)
        self.text_SUBJECT = Entry(frame_subject, width=40)
        self.text_SUBJECT.pack(side = LEFT, expand = True, fill = X)
        self.text_SUBJECT.insert(0, self.template_subject)
        
        frame_body = ttk.Frame(main_top_frame)
        frame_body.pack(side = TOP, expand = False, fill = BOTH, padx=5, pady=5)
        lblBody = ttk.Label(frame_body, text="Body: ")
        lblBody.pack(side = LEFT, expand = False, fill = X, padx=5, pady=5)
        self.text_BODY = Text(frame_body, width = 40, height = 5)
        S = Scrollbar(frame_body, command=self.text_BODY.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_BODY.configure(yscrollcommand=S.set)
        self.text_BODY.pack(side = LEFT, expand = True, fill = BOTH)
        
        self.text_BODY.insert(1.0, self.template_body)
 
        ################ Bottom FRAME ##############
        frame_bottombuttons = ttk.Frame(self.root)
        frame_bottombuttons.pack(side=BOTTOM, fill=X, expand = False,)
        frame_bottombuttons.config(relief = RIDGE, borderwidth = 0)    
           
         # Button To Clear To: Details
        button_clearform_EGM= ttk.Button(frame_bottombuttons, text = "Clear Form", width = 20,command = lambda: self.handleButtonPress('__clear_form_egm__'))                                             
        button_clearform_EGM.grid(row=0, column=0,  sticky='s',  padx=5, pady=5)
        
        button_refreshform = ttk.Button(frame_bottombuttons, text = "Refresh Email Template", width = 20,command = lambda: self.handleButtonPress('__refresh__'))                                             
        button_refreshform.grid(row=0, column=1,  sticky='s',  padx=5, pady=5)

    def DrawCheckButtons(self): 
        self.vars_editor = []
        ## cc: checkboxes
        for i in range(len(self.email_groups_list_editor)):
            var = IntVar()
            ttk.Checkbutton(self.frame_JSON_View.interior, text=str(self.email_groups_list_editor[i]), variable =var, onvalue=1, offvalue=0).pack(side=TOP, anchor='w', expand=True)
            self.vars_editor.append(var)
           
    def HandleRadioButton(self):
        # 1 clear the canvas. 
        self.frame_JSON_View.destroy()
        self.generateEmailGroupsEditor()
        self.frame_JSON_View = ScrollableFrame(self.frame_Address)
        self.frame_JSON_View.config(relief = RIDGE, borderwidth = 1)
        self.frame_JSON_View.pack(side = RIGHT, fill=Y, expand = False)
        self.DrawCheckButtons()

    def handleButtonPress(self, event):
        self.template_body =  self.text_BODY.get(1.0, END)
        self.template_subject = self.text_SUBJECT.get()
        
        if event == '__button_cc_apply_egm__':
            self.generateEmailGroupsEditor()
            self.text_JSONoutput.delete(1.0, END) # Clear the field
            for i in range(len(self.vars_editor)):
                if (self.vars_editor[i].get() == 1):
                    self.cc_address_list.append(self.email_groups_list_editor[i])
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
                    
        elif event == '__button_to_apply_egm__':
            self.generateEmailGroupsEditor()
            self.text_JSONoutput.delete(1.0, END) # clear
            for i in range(len(self.vars_editor)):
                if (self.vars_editor[i].get() == 1):
                    # Save Keys related to self.vars_editor_egm
                    self.to_address_list.append(self.email_groups_list_editor[i])
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__button_bcc_apply_egm__':
            self.generateEmailGroupsEditor()
            self.text_JSONoutput.delete(1.0, END) # clear
            for i in range(len(self.vars_editor)):
                if (self.vars_editor[i].get() == 1):
                    self.bcc_address_list.append(self.email_groups_list_editor[i])
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__button_cc_clear_egm__':
            for i in range(len(self.vars_editor)):
                self.vars_editor[i].set(0)
            self.cc_address_list[:] = []
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__button_to_clear_egm__':
            for i in range(len(self.vars_editor)):
                self.vars_editor[i].set(0)
            self.to_address_list[:] = []
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__button_bcc_clear_egm__':
            for i in range(len(self.vars_editor)):
                self.vars_editor[i].set(0)
            self.bcc_address_list[:] = []
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__clear_form_egm__':
            self.text_JSONoutput.delete(1.0, END) # Clear the field
            self.combobox_box_Template_EGM.set("1. Select a Template...")       

            self.template_subject = DEFAULT_SUBJECT
            self.template_body = DEFAULT_BODY
            self.to_address_list[:] = []
            self.bcc_address_list[:] = []
            self.cc_address_list[:] = []

            for i in range(len(self.vars_editor)):
                self.vars_editor[i].set(0)
                
            #self.HandleRadioButton()    
            self.text_JSONoutput.delete(1.0, END)
            self.text_SUBJECT.delete(0,END)
            self.text_BODY.delete(1.0,END)
            
            self.vars_editor_rb_mode_editor.set(3) # All filter

        elif event == '__refresh_email_list_egm__':
            self.combobox_box_Template_EGM['values'] =  self.generateTemplateList() # generate values based on Template List
        elif event == '__save_template_egm__':
            self.saveTemplate(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)
        elif event == '__refresh__':
            self.generateJSONObject_to_Display(self.to_address_list,  self.cc_address_list,  self.bcc_address_list, self.template_body, self.template_subject)

    def handleComboBoxChanges(self, event):
        self.text_JSONoutput.delete(1.0, END)

        template = ''
        self.template_json_data = ''
        _templateChoice = self.combobox_box_Template_EGM.get()
        if _templateChoice in self.generateTemplateList():
            self.template_json_data = self.readEmailTemplate(_templateChoice) # Read Template Data and return the JSON data object
        else:
            print("could not read file: " + _templateChoice)
        
        self.generateEmailGroupsEditor()
        
        self.to_address_list = self.template_json_data['Email Template']['to']
        self.cc_address_list = self.template_json_data['Email Template']['cc']
        self.bcc_address_list = self.template_json_data['Email Template']['bcc']
        
        self.template_subject = self.template_json_data['Email Template']['subject']
        self.template_body = self.template_json_data['Email Template']['body']
        
        self.text_BODY.delete(1.0, END)
        self.text_BODY.insert(1.0, self.template_body)
        self.text_SUBJECT.delete(0, END)
        self.text_SUBJECT.insert(0, self.template_subject)

        self.text_JSONoutput.insert(1.0,json.dumps(self.template_json_data, indent=4, sort_keys=True, separators=(',',':'))) 
        
    def generateEmailGroupsEditor(self): 
        self.email_groups_list_editor = list() 
        if self.vars_editor_rb_mode_editor.get() == 1: #  EGM mode 
            # Generate the Email Group List
            for k,v in self.data.items(): # set defaults
                if str(k).startswith("SYS"):
                    pass # ignore 
                else:
                    self.email_groups_list_editor.append(k)
        elif self.vars_editor_rb_mode_editor.get() == 2: # SYS mode
            for k,v in self.data.items(): # set defaults
                if str(k).startswith("EGM"):
                    pass # ignore 
                else:
                    self.email_groups_list_editor.append(k)
        else: # ALL Filter
            for k,v in self.data.items(): # set defaults
                self.email_groups_list_editor.append(k)
 
        self.email_groups_list_editor.sort()
    
    
def main():
    app = TemplateEditor()

if __name__ == "__main__": main()
