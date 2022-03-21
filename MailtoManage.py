#!/usr/bin/python3

import json
import os
import sys
import shlex
import getpass
import hashlib
from datetime import datetime
import re

from tkinter import *
from tkinter import ttk, messagebox
from mailto import mailto

VERSION = "0.8"

USE_ENCODED_DATA = False
# if encoded data we use: 
FILENAME = "emaildata_v2.json"
LOOKUPTABLE_FILE = "emaildata_lookup.json"
# otherwise just use: 
FILENAME_NON_ENCODED = "emaildata.json"  # this is the output filename of the iNetToMailtoFormat.py script

# the following is required for authentication (currently disabled)
NUMBER_OF_ATTEMPTS = 3
VALID_PASSWORDS = ["63f6a3533a1d65ea4cc016ef2371c09bce7a00b3d4495e2cf6eec18d4083e1f0", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]

# EMAIL_ADDRESS_REGEX = re.compile(r"\A[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\z")

# v0.8
# added last modified date of FILENAME to header
# added support to disable encoded data via USE_ENCODED_DATA
#   this was added to remove difficuly in reconciliation with processing iNET FM14 version. 

# v0.7 
# relax email address verification to cater for printable characters. 

# v0.6
# Disable password check 
# As per directives in QMS Memo: 29/7/2020

# v0.5
# Adds proper email address regex validations
# v0.4
# Adds password protection to class as opposed to script

# v0.3
# Adds support to hashed email addresses in emaildata_v2.json
#
# v0.2
# Includes functions for validations of email addresses in the emaildata.json file
#   - validates that all email addresses are the same (if used in more than one email group).
#   - validate email format is correct
#   - email addresses has timestamps. 
#   - prompts to validate email groups that haven't been updated for X months

# Specific Email Groups, validations:
#   - Hashes of Email Groups are generated and used for comparison to ensure that it hasn't changed [done]
#   - from last known group.
# MailManage - adds user restrictions
# 

## Expected Format for JSON object:
##{
##	"Email Details": [{
##		"Email Hash": "4edd12c75a2f0887b28ea30a884c644f9f1e8809ed3b496a4aaf663e454ddb9e",
##		"Group": "EGM IGT"
##	}, {
##		"Email Hash": "c2c28fe5615f9a842cfa3dc7d0274d231177558a33b78625f31de954486c510c",
##		"Group": "Reef Casino"
##	}]
##}

class GetPwd:

    def __init__(self): 
        self.my_root = Tk()
        self.my_root.wm_title("MailtoManage.py: Correct Priviledges Required")
        self.pwdbox = Entry(self.my_root, show = '*', width=40, font=("Arial", 18))

        Label(self.my_root, text = 'Changing Email Groups now requires a Password:', width=40, font=("Arial", 18)).pack(side = 'top')
        
        self.pwdbox.pack(side = 'top')
        self.pwdbox.bind('<Return>', self.onpwdentry)
        Button(self.my_root, command=self.onokclick, text = 'OK', width=10, padx=3, pady=3).pack(side = 'top')

        self.my_root.protocol("WM_DELETE_WINDOW", self.disable_event)

        self.my_root.mainloop()

    def disable_event(self): 
        pass
    
    def onpwdentry(self, evt):
        self.password = self.pwdbox.get()
        self.my_root.destroy()
    
    def onokclick(self):
        self.password = self.pwdbox.get()
        self.my_root.destroy()
    
    def get(self): 
        return self.password
        
class MailtoManage:

    # Constructor
    def __init__(self):

        # Disable password check               
        #if self.authorise(): 
        if True:
            self.data = ''
            self.emailaddressheaders = []

            if USE_ENCODED_DATA:
                self.EmailGroupAddress_hashlist = []
                self.datafilename = FILENAME
                self.emailaddressheaders = self.readfile(self.datafilename)
                self.lookuptablefilename = LOOKUPTABLE_FILE                
                self.email_lookup_table = mailto.ReadJSONfile(self, self.lookuptablefilename)

                if (self.validatefile(self.datafilename, self.data)): 
                    print("Email Data file integrity: OK")
                else:
                    # Automatically Generate Signature JSON file
                    self.generateSignatureJSONfile(self.datafilename, self.data)
                    print("FYI: Generated new Email Group Signature File")
                    # sys.exit(2)                
            else:
                self.datafilename = FILENAME_NON_ENCODED
                self.emailaddressheaders = self.readfile(self.datafilename)

            ## All good, display GUI. 
            self.mygui = Tk()
            self.mygui.focus_force()
            self.setupGUI()
        else: 
            sys.exit("Incorrect Password, terminating...")

    def authorise(self): 
        pass_try = 0
        x = NUMBER_OF_ATTEMPTS
        
        while pass_try < x:
            getpwd = GetPwd()
            
            password = hashlib.sha256(getpwd.get().encode()).hexdigest()

            #m = hashlib.sha256(getpwd().encode())
            #hashlist_emailAddress_list.append(m.hexdigest())
            #print("password entered is: " + password)

            # Blank password: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
            # My Password: 63f6a3533a1d65ea4cc016ef2371c09bce7a00b3d4495e2cf6eec18d4083e1f0
           
            if password in VALID_PASSWORDS: 
                pass_try = x+1
            else:
                pass_try += 1
                print("Incorrect Password!", "Invalid Password entered. " + str(x-pass_try) + " more attempts left. \nRefer to James Aceret (3872 0804) for help on this issue.")

        if pass_try == x:
            return False

        print("User password valid.")
        return True
        
    def generateSignatureJSONfile(self, fname, data):
        # Read the fname file,
        # Regenerate the Email Signature JSON object
        # Overwrite the previous signature json file with the new version.

        # self.data = None # Reinitialise
        # self.readfile(fname)

        with open(fname+"_sigs.json", 'w') as jsonsigs_outfile: # overwrite
            # Generate Email Group Hashes in self.Generated_EmailDetails_list
            Generated_EmailDetails_list = self.generateEmailGroupHashes(data)

            # Write to JSON file
            jsonsigs_outfile.write(json.dumps(Generated_EmailDetails_list, indent=4, separators=(',',':')))
                
    def readfile(self, filename):
        emailaddressheaders = [] # reset
        self.data = mailto.ReadJSONfile(self, filename)       
        for k, v in self.data.items():
            emailaddressheaders.append(k)

        return emailaddressheaders

    def generateEmailGroupHashes(self, data):
        Generated_EmailDetails_list = []
        
        # Generate Hashes for each Email Group in the file.
        # SUPER TOP SECRET INDUSTRY EYES ONLY - DO NOT READ HERE"
        for k,v in data.items():
            Generated_EmailDetails_list.append({ 'Email Group' : k,
                                                      'Email Hash': self.generatehash_list(v),
                                                      #'Timestamp': str(datetime.now()),
                                                      #'Generated': getpass.getuser()
                                                      }) # as v is a List. 

        for item in Generated_EmailDetails_list:
            item['Email Hash'] = ''.join(item['Email Hash'])            # Turn Hash List into a single string
            item['Email Hash'] = self.generatehash(item['Email Hash'])  # replace HashString as a hash, by Hashing the string. 

        return Generated_EmailDetails_list
        
    def validatefile(self, filename, data):
        JSONfilename = filename+"_sigs.json"
        
        #data = {}
        #data['Email Details'] = []
        self.Generated_EmailDetails_list = [] # json.dumps(data)
        
        if (os.path.isfile(JSONfilename)):
            print("Checking if file: " + JSONfilename + " exists...")
            with open(JSONfilename, 'r') as json_file:
                print("...File Exist...")
                print("Loading data...")
                EmailDetails_List = json.load(json_file) # Return JSON object: "Email Details"
                print("Complete.")
                
                # GenerateEmailGroup Hashes
                Generated_EmailDetails_list = self.generateEmailGroupHashes(data)

                # Verify the integrity of the JSON file, i.e. match Hashes in file against generated versions
                if (sorted(json.dumps(EmailDetails_List)) == sorted(json.dumps(Generated_EmailDetails_list))):
                    return True
                else:
                    return False
                    
                # Uncomment below line to display generated Email Group Hashes()
                # self.printJSONobjectlist(self.Generated_EmailDetails_list) 

        else:
            print(JSONfilename +" cannot be found. Generating hashes for: " + filename)
            return(False)

        return(False)

    def printJSONobjectlist(self, ListedObject):
        for item in ListedObject:
            print(json.dumps(item, indent=4, separators=(',',':')))

    def generatehash_list(self, EmailAddressText_list):
        hashlist_emailAddress_list = []
        # to do generate hashes from email address string.
        for item in EmailAddressText_list:
            m = hashlib.sha256(item.encode())
            hashlist_emailAddress_list.append(m.hexdigest())
            
        return hashlist_emailAddress_list

    def generatehash(self, mytext):
        m = hashlib.sha256(mytext.encode())
        return m.hexdigest()

    def lastModifiedDate(self, fname): 
        lastmodified= os.stat(fname).st_mtime

        # 2017-06-03 02:17:48.263740        
        return datetime.fromtimestamp(lastmodified) 

    def setupGUI(self):
        self.mygui.wm_title("MailtoManage v" + str(VERSION) + " - " + self.datafilename + " - Last Modified Date: " + str(self.lastModifiedDate(self.datafilename)))
        self.mygui.resizable(1,1)      

        frame_toparea = ttk.Frame(self.mygui)
        frame_toparea.pack(side = TOP, fill=X, padx=5, pady=5, expand=False)
        
        frame_Header = ttk.Labelframe(frame_toparea, text = "Quick HOWTO: \nUse this form to edit the Email Addresses stored in the JSON file, use a new line for each entry, no commas.")
        frame_Header.pack(side = TOP, padx = 5, pady=5, fill=X, expand = True)
        
        # Combo Box for Template
        self.cbEmailAddress = StringVar()
        self.combobox_box_EmailAddress = ttk.Combobox(frame_Header, justify=LEFT, textvariable=self.cbEmailAddress, width = 50, state='normal')
        self.combobox_box_EmailAddress.pack(side = LEFT, padx=5, pady=5)
        self.combobox_box_EmailAddress.set('Select Email Group to edit Email Addresses')
        self.combobox_box_EmailAddress['values'] = sorted(self.emailaddressheaders)
        self.combobox_box_EmailAddress.bind('<<ComboboxSelected>>', self.handleComboBoxchanges)

        # Button To Contacts Apply
        button_template= ttk.Button(frame_Header, text = "Save Changes", width = 20,command = lambda: self.handleButtonPress('__selected_save_changes__'))                                             
        button_template.pack(side=LEFT, padx=5,pady=5)

        # Button Refresh Email Groups
        button_refresh= ttk.Button(frame_Header, text = "Refresh", width = 20,command = lambda: self.handleButtonPress('__refresh_groups__'))                                             
        button_refresh.pack(side=LEFT, padx=5,pady=5)
        
        # Button Delete Email Groups
        button_refresh= ttk.Button(frame_Header, text = "Delete Email Group", width = 20,command = lambda: self.handleButtonPress('__delete_group__'))                                             
        button_refresh.pack(side=LEFT, padx=5,pady=5)        
        
        # Need to use .pack() for scrollbar and text widget
        frame_textarea = ttk.Labelframe(self.mygui, text="Email Details")
        frame_textarea.pack(side = TOP, fill = BOTH, expand = True, padx=5, pady=5)
        frame_textarea.config(relief = RIDGE, borderwidth = 0)

        # Text Area for Addresses
        self.text_Addresses = Text(frame_textarea, height = 30)
        S = Scrollbar(frame_textarea, command=self.text_Addresses.yview)
        S.pack(side=RIGHT, fill=Y)
        self.text_Addresses.configure(yscrollcommand=S.set)
        self.text_Addresses.pack(side=LEFT, fill=BOTH, expand = True)

        self.bottom_screen_status = ttk.Label(self.mygui, text="Ready...")
        self.bottom_screen_status.pack(side=BOTTOM, fill = X, expand = False, padx=5, pady=5)

        self.mygui.mainloop()
    
    def handleComboBoxchanges(self, event):
        self.RefreshEmailGroups() 
        
        self.text_Addresses.delete(1.0, END)
        _UserChoice = self.combobox_box_EmailAddress.get()
        if USE_ENCODED_DATA: 
            email_lookup_table = mailto.ReadJSONfile(self, self.lookuptablefilename)
            for entry in self.data.get(_UserChoice):
                entry = email_lookup_table[entry]
                self.text_Addresses.insert(END, entry.rstrip(" ").rstrip(";")+"\n")
        else: 
            for entry in self.data.get(_UserChoice):
                self.text_Addresses.insert(END, entry.rstrip(" ").rstrip(";")+"\n")
    
    def Backup_EmailFile(self, fname):
        if (os.path.isfile(fname)): 
            with open(fname, 'r') as json_file:
                data = json.load(json_file)
                unix_timestamp = datetime.now().timestamp() # include timestamp in file name and user
                fname_backup = "backup/" + fname+ "_" + str(unix_timestamp) + "_" + getpass.getuser() +".backup"
                with open(fname_backup,'w+') as json_file:
                    json.dump(data, json_file, sort_keys=True, indent=4, separators=(',',':'))
            
            self.bottom_screen_status.config(text = "Backup of: '" + fname + "' saved to: " + fname_backup)
        else:
            print(fname + " cannot be found. Generating default file...")
            return False
        return True
        
    def handleButtonPress(self, input):
        self.RefreshEmailGroups()         
        
        if self.Backup_EmailFile(self.datafilename):
            print("Automatically saving a backup of last: " + self.datafilename)
        else: 
            print("Error saving a backup of file: " + self.datafilename)
        
        if USE_ENCODED_DATA: 
            if self.Backup_EmailFile(self.lookuptablefilename):
                print("Automatically saving a backup of last: " + self.lookuptablefilename)
            else: 
                print("Error saving a backup of file: " + self.lookuptablefilename)
        
        if input == '__selected_save_changes__':
            updated_addr = self.text_Addresses.get(1.0, 'end-1c').split("\n")
            updated_addr = [x for x in updated_addr if x !=''] # remove empty strings. 

            # Update the record. 
            choice_email_group = self.combobox_box_EmailAddress.get()

            # 2. Create new Dict Entry for Manufacturer & Replace dictionary entry with new version
            # Verify if user choice already exists if so continue otherwise, 
            # Present an option to create a new Email Group
            
            hashed_addr_list = list() 
            for address in updated_addr: 
                # clean email address: 
                address = re.sub(';', '', address.lower()) # remove semicolons and tolower() 
                # filter out just email address
                # match = re.findall(r'[\w\.-]+@[\w\.-]+', address)        
                match = re.findall(r'[^@]+@[^@]+\.[^@]+', address)                        
                # match = re.findall(r'''\A[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\z''', address)                          
                # match = re.findall()
                if USE_ENCODED_DATA:           
                    hashed_email_address = hashlib.sha256(str(match[0]).encode('utf-8')).hexdigest() # use SHA1 hashes and save this 
                    print(match[0], hashed_email_address)
                    hashed_addr_list.append(hashed_email_address)
                    
                    # Update lookup table. 
                    self.email_lookup_table[hashed_email_address] = match[0]

                    # remove duplicate email addresses          
                    self.data[choice_email_group] = list(set(hashed_addr_list))
                else: 
                    self.data[choice_email_group] = list(set(updated_addr))
                            
            # 4. Save to disk. 
            self.SaveDatatoDisk()         
                
            # Update the Email Signature JSON file
            # Read the EmailData.json file,
            # Regenerate the Email Signature JSON object
            # Overwrite the previous signature json file with the new version.

            if USE_ENCODED_DATA:           
                self.generateSignatureJSONfile(self.datafilename, self.data)
        
        elif input == '__refresh_groups__':
            self.RefreshEmailGroups() 
            
        elif input == '__delete_group__': 
            choice_email_group = self.combobox_box_EmailAddress.get()
            userChoice = messagebox.askokcancel("Warning! Deleting Email Groups!", "Are you sure you want to remove " + choice_email_group + "?")
            if userChoice:
                del self.data[choice_email_group] 
                self.SaveDatatoDisk()      
                self.RefreshEmailGroups() 
                if USE_ENCODED_DATA:
                    self.generateSignatureJSONfile(self.datafilename, self.data)

    def SaveDatatoDisk(self): 
        with open(self.datafilename, 'w') as json_file: #over-write file
            json.dump(self.data, json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 

        if USE_ENCODED_DATA:
            with open(self.lookuptablefilename, 'w+') as lookup_json_file: 
                json.dump(self.email_lookup_table, lookup_json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 
                
    def RefreshEmailGroups(self):
        self.emailaddressheaders = self.readfile(self.datafilename)
        self.combobox_box_EmailAddress['values'] = sorted(self.emailaddressheaders)        

    # Joins a string with commas.        
    def formatEmailAddress(self, str):
        return(','.join(shlex.split(str)))

def main():
    app = MailtoManage()
      

if __name__ == "__main__": main()
