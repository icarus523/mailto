# https://stackoverflow.com/questions/6325216/parse-html-table-to-python-list
# https://pbpython.com/pandas-html-table.html

import json
import pandas as pd
import numpy as np
from unicodedata import normalize

# input_file is a JSON file format that needs to be formatted as a dict 
# to support mailto script. 
INPUT_FILE = 'storage_format.html'

class HTMLParser: 

    def __init__(self, fname): 
        self.WriteDatatoFile(self.readHTML(fname))

    def readHTML(self, fname): 
        table_read = pd.read_html(fname, match='Email Groups')
        print(f'Total tables: {len(table_read)}')

        self.df = table_read[0]

        return self.df.to_json(orient='records') 

    def WriteDatatoFile(self, json_d): 
        #export JSON file
        with open('storage_format.json', 'w+') as f:
            f.write(json_d)

def main():
    app = HTMLParser(INPUT_FILE)

if __name__ == "__main__": main()
