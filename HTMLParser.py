# https://stackoverflow.com/questions/6325216/parse-html-table-to-python-list
# https://pbpython.com/pandas-html-table.html
import json
import pandas as pd
import numpy as np
import requests
import json
import base64

from unicodedata import normalize

URL = "https://inet-olgr.justice.qld.gov.au/plugins/viewstorage/viewpagestorage.action?pageId=48334101"
USE_JAMES_CREDENTIALS = True

# input_file is a JSON file format that needs to be formatted as a dict 
# to support mailto script. 
HTML_fname = 'storage_format.html'
JSON_FNAME = 'storage_format.json'

class HTMLParser: 

    def __init__(self): 
        self.credentials = ''

        if USE_JAMES_CREDENTIALS:
            self.downloadHTML(URL)
        else: 
            self.promptForCredentials()
            self.downloadHTML(URL, self.credentials)

        self.WriteDatatoFile(JSON_FNAME, self.readHTML(HTML_fname))

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
           verify=False # ignore SSL errors
        )

        # save to disk
        self.WriteDatatoFile(HTML_fname, response.text)

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
