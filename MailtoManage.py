#!/usr/bin/python3

import json
import os, sys
import mailto
import shlex
import getpass
import hashlib
from datetime import datetime

from tkinter import *
from tkinter import ttk

FILENAME = "emaildata.json"
VERSION = "0.2"
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

class MailtoManage:

    # Constructor
    def __init__(self):
        
        self.data = ''
        self.emailaddressheaders = []
        self.EmailGroupAddress_hashlist = []
        self.readfile(FILENAME)
        
        if (self.validatefile(FILENAME)): 
            print("Email Data file integrity: OK")
        else:
            # Automatically Generate Signature JSON file
            self.generateSignatureJSONfile()
            print("Generated new Email Group Signature File, please start again")
            sys.exit(2)

        ## All good, display GUI. 
        self.mygui = Tk()
        self.mygui.focus_force()
        self.setupGUI()

    def generateSignatureJSONfile(self):
        # Read the EmailData.json file,
        # Regenerate the Email Signature JSON object
        # Overwrite the previous signature json file with the new version.

        self.data = None # Reinitialise
        self.readfile(FILENAME)

        with open(FILENAME+"_sigs.json", 'w') as jsonsigs_outfile: # overwrite
            # Generate Email Group Hashes in self.Generated_EmailDetails_list
            Generated_EmailDetails_list = self.generateEmailGroupHashes(self.data)

            # Write to JSON file
            jsonsigs_outfile.write(json.dumps(Generated_EmailDetails_list, indent=4, separators=(',',':')))
                

    def readfile(self, filename):
        self.data = mailto.mailto.ReadJSONfile(self, filename)       
        for k, v in self.data.items():
            self.emailaddressheaders.append(k)

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
        
    def validatefile(self, filename):
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
                Generated_EmailDetails_list = self.generateEmailGroupHashes(self.data)

                #Verify the integrity of the JSON file, i.e. match Hashes in file against generated versions
                if (sorted(json.dumps(EmailDetails_List)) == sorted(json.dumps(Generated_EmailDetails_list))):
                    return True
                else:
                    messagebox.showerror("JSON Signature file cannot be verified", "Integrity of JSON sigs file failed to be verified. \n\nAborting & Exiting. \n\nRefer to James Aceret (3872 0804) for help on this issue.")
                    print("Integrity of JSON sigs file failed to be verified. Aborting.")
                    sys.exit(2)
                    
                # Uncomment below line to display generated Email Group Hashes()
                #self.printJSONobjectlist(self.Generated_EmailDetails_list) 

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

    def setupGUI(self):
        self.mygui.wm_title("Email Group Address Manager")
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
        self.text_Addresses.delete(1.0, END)
        _UserChoice = self.combobox_box_EmailAddress.get()
    
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
            return(1) 
        return(0)
        
    def handleButtonPress(self, input):
        self.readfile(FILENAME)
        
        if self.Backup_EmailFile(FILENAME) == 0:
            print("Automatically saving a backup of last: " + FILENAME)
        else: 
            print("Error saving a backup of file: " + FILENAME)
        
        if input == '__selected_save_changes__':
            updated_addr = self.text_Addresses.get(1.0, 'end-1c').split("\n")
            updated_addr = [x for x in updated_addr if x !=''] # remove empty strings. 

            # Validate Email Strings: 
                        
            # Update the record. 
            _UserChoice_key = self.combobox_box_EmailAddress.get()

            # 2. Create new Dict Entry for Manufacturer & Replace dictionary entry with new version
            # Verify if user choice already exists if so continue otherwise, 
            # Present an option to create a new Email Group
            self.data[_UserChoice_key] = updated_addr
            
            # 4. Save to disk. 
            print('Saving changes to json file: ' + FILENAME)
            with open(FILENAME, 'w') as json_file: #over-write file
                json.dump(self.data, json_file, sort_keys=True, indent=4, separators=(',',':')) # write to disk. 

            # Update the Email Signature JSON file
            # Read the EmailData.json file,
            # Regenerate the Email Signature JSON object
            # Overwrite the previous signature json file with the new version.

            self.generateSignatureJSONfile()

        self.readfile(FILENAME)
            
    # Joins a string with commas.        
    def formatEmailAddress(self, str):
        return(','.join(shlex.split(str)))

PASSWORD = ''
def getpwd():
    global PASSWORD
    
    root = Tk()
    root.wm_title("Correct Priviledges Required")
    pwdbox = Entry(root, show = '*')
    def onpwdentry(evt):
         global PASSWORD
         PASSWORD = pwdbox.get()
         root.destroy()
    def onokclick():
         global PASSWORD
         PASSWORD = pwdbox.get()
         root.destroy()
    Label(root, text = 'Enter Password:', width=80).pack(side = 'top')

    pwdbox.pack(side = 'top')
    pwdbox.bind('<Return>', onpwdentry)
    Button(root, command=onokclick, text = 'OK').pack(side = 'top')

    root.mainloop()
    return PASSWORD

def main():
    pass_try = 0
    x = 3

    while pass_try < x:
        password = hashlib.sha256(getpwd().encode()).hexdigest()

        #m = hashlib.sha256(getpwd().encode())
        #hashlist_emailAddress_list.append(m.hexdigest())
        # print("password entered is: " + password)

        # Blank password: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
        # My Password: 63f6a3533a1d65ea4cc016ef2371c09bce7a00b3d4495e2cf6eec18d4083e1f0

        valid_passwords = ["63f6a3533a1d65ea4cc016ef2371c09bce7a00b3d4495e2cf6eec18d4083e1f0", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]
        
        if password in valid_passwords: 
            pass_try = x+1
        else:
            pass_try += 1
            print("Incorrect Password!", "Invalid Password entered. " + str(x-pass_try) + " more attempts left. \nRefer to James Aceret (3872 0804) for help on this issue.")

    if pass_try == x:
        sys.exit("Incorrect Password, terminating...")

    print("User password valid.")
    app = MailtoManage()
      

if __name__ == "__main__": main()
