# https://stackoverflow.com/questions/6325216/parse-html-table-to-python-list
# https://pbpython.com/pandas-html-table.html
import json
import pandas as pd
import numpy as np
import requests
import json
import base64

from unicodedata import normalize
from tkinter import *

URL = "https://inet-olgr.justice.qld.gov.au/plugins/viewstorage/viewpagestorage.action?pageId=48334101"
SUCCESS_CODE = 200
USE_JAMES_CREDENTIALS = False
INET_CERT = "certs/inet-olgr-justice-qld-gov-au-chain.pem"

# input_file is a JSON file format that needs to be formatted as a dict 
# to support mailto script. 
HTML_fname = 'storage_format.html'
JSON_FNAME = 'storage_format.json'

class HTMLParser: 

    def __init__(self): 
        self.credentials = ''
        
        self.parsed_website = False

        if USE_JAMES_CREDENTIALS:
            self.parsed_website = self.downloadHTML(URL)
            if self.parsed_website: 
                self.WriteDatatoFile(JSON_FNAME, self.readHTML(HTML_fname))            
            else:
                print("error parsing: " + url)
        else: 
            self.promptForCredentials() # display GUI

    def promptForCredentials(self): 
        self.root = Tk()
        self.root.title("HTMLParser")
        width = 400
        height = 250
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry("%dx%d+%d+%d" % (width, height, x, y))
        self.root.resizable(0, 0)

        #==============================VARIABLES======================================
        self.username = StringVar()
        self.password = StringVar()
         
        #==============================FRAMES=========================================
        Top = Frame(self.root, bd=2,  relief=RIDGE)
        Top.pack(side=TOP, fill=X)
        Form = Frame(self.root)
        Form.pack(side=TOP, pady=20)
         
        #==============================LABELS=========================================
        lbl_title = Label(Top, text = "HTMLParser: Login to iNET", font=('arial', 15))
        lbl_title.pack(fill=X)
        lbl_username = Label(Form, text = "Username:", font=('arial', 14), bd=15)
        lbl_username.grid(row=0, sticky="e")
        lbl_password = Label(Form, text = "Password:", font=('arial', 14), bd=15)
        lbl_password.grid(row=1, sticky="e")
        self.lbl_text = Label(Form)
        self.lbl_text.grid(row=2, columnspan=2)
         
        #==============================ENTRY WIDGETS==================================
        username = Entry(Form, textvariable=self.username, font=(14))
        username.grid(row=0, column=1)
        password = Entry(Form, textvariable=self.password, show="*", font=(14))
        password.grid(row=1, column=1)
         
        #==============================BUTTON WIDGETS=================================
        btn_login = Button(Form, text="Login", width=30, command=self.Login)
        btn_login.grid(pady=10, row=3, columnspan=2)
        btn_login.bind('<Return>', self.Login)

        self.root.mainloop()

    def Login(self, event=None):
        if self.username.get() == "" or self.password.get() == "":
            self.lbl_text.config(text="Please complete the required field!", fg="red")
        else:
            self.root.withdraw() # hide
            auth_str = self.generate_auth_str(self.username.get(), self.password.get())

            if self.downloadHTML(URL, auth_str): 
                self.WriteDatatoFile(JSON_FNAME, self.readHTML(HTML_fname))            
            else:
                print("error parsing: " + URL)

    def generate_auth_str(self, login, password): 
        auth_str = login + ":" + password
        # need to encode Authentication string to base64
        encodedBytes = base64.b64encode(auth_str.encode("utf-8"))
        encodedStr = str(encodedBytes, "utf-8")

        return encodedStr
        
    def downloadHTML(self, url, auth_str='YWNlcmV0anI6OTNudVl3aER4W1Uo'): 
        # auth_str: if its good enough for Tabcorp, its good enough for me

        headers = {
           "Content-Type": "application/json",
           "Authorization": "Basic " + auth_str
        }

        response = requests.request(
           "GET",
           url,
           headers=headers,
           verify=INET_CERT,
        )

        if response.status_code == SUCCESS_CODE: 
            print("Server Response: ", response.status_code, " success! retrieved data from: ", response.url, )
            self.WriteDatatoFile(HTML_fname, response.text)
            return True
        else:
            print("Server Response: ", response.status_code, " failure! reason:", response.reason)
            return False

    def readHTML(self, fname): 
        table_read = pd.read_html(fname, match='Email Groups')
        print(f'Total tables: {len(table_read)}')

        self.df = table_read[0]
        print(self.df.info())
        
        return self.df.to_json(orient='records') 

    def WriteDatatoFile(self, fname, data): 
        with open(fname, 'w+') as f:
            f.write(data)

def main():
    app = HTMLParser()

if __name__ == "__main__": main()
