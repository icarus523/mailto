import itertools
import json
import os
import re
import sys
import unicodedata
import json
import pandas as pd

from mailto import mailto
from MailtoDataEncode import MailtoDataEncode
from HTMLParser import HTMLParser

INPUT_FILE_NAME = 'storage_format.html'
OUTPUT_FILE_NAME = 'emaildata.json'
USE_ENCODED_DATA = False

# description:  convert the table entry for Mailto Email Groups in iNET to the mailto dictionary, 
#               and then create the appropriate files (lookup). 
 
# Procedure is: 
# 1. Login to iNET at # https://inet-olgr.justice.qld.gov.au/display/TECH/Contact+Lists#ContactLists-MailtoEmailGroups
# 2. in INET select "View Storage Format"
# 3. Export to HTML and save as "storage_format.html"
# 4. Run this script to produce "sample_converted.json"
# 5. This will also run MailtoDataEncode to produce: "sample_emaildata_lookup.json" and "sample_emaildata_v2.json"
# 6. compare differences and merge with existing 'emaildata_lookup.json' and 'emaildata_v2.json' file

# stripping non printable characters from string
# ref: https://stackoverflow.com/questions/92438/stripping-non-printable-characters-from-a-string-in-python
all_chars = (chr(i) for i in range(sys.maxunicode))
categories = {'Cc'}
control_chars = ''.join(c for c in all_chars if unicodedata.category(c) in categories)
# or equivalently and much more efficiently
control_chars = ''.join(map(chr, itertools.chain(range(0x00,0x20), range(0x7f,0xa0))))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

class iNetToMailtoFormat: 

    def __init__(self): 
        # read HTML and save JSON to disk
        self.parser = HTMLParser()
        if self.parser.parsed_website: 
            self.data = self.convertJSON(mailto.ReadJSONfile(self, 'storage_format.json'))

            # sort
            for k,v in self.data.items():
                self.data[k] = sorted(v)
            
            # 'self.data' should now be in the expected dict format
            # print(json.dumps(self.data, sort_keys=True, indent=4, separators=(',',':')))

            # save to disk
            MailtoDataEncode.WriteDatatoFile(self, self.data, OUTPUT_FILE_NAME)
            os.remove('storage_format.json') # remove temp file, after pretty print

            # now generate the required encoded files for the mailto script
            if USE_ENCODED_DATA == True: 
                MailtoDataEncode(OUTPUT_FILE_NAME)
        else: 
            print("Error parsing iNet website.")

    def remove_control_chars(self, s):
        return control_char_re.sub('', s)

    def convertJSON(self, json_data): 
        converted_data_d = dict() 

        for item in json_data:
            email_addr_l = list()
            # clean up the email address string

            # due to: regulatory.lotterieskeno&gaming@tabcorp.com.au;
            # HTML converts this string to 'regulatory.lotterieskeno&amp;gaming@tabcorp.com.au';
            # however the following process will escape the &. so this will replace '&amp;' 
            # with the original characer '&'
            address_s = item['Contact Email Address'].replace('&amp;', '&')
            # turn the string to a list, while removing any non-printable characters, i.e. \n\r
            address_l = self.remove_control_chars(address_s).split(';')
            # remove starting spaces in the list
            address_l = map(str.lstrip, address_l)             
            # remove empty strings.
            address_l = [x for x in address_l if x !='']  
            # sort address_l
            address_l = sorted(address_l)
            # add to the dict output
            # handle & in email group name
            converted_data_d[item['Email Groups'].strip().replace('&amp;', '&')] = address_l
            
        return converted_data_d

def main():
    app = iNetToMailtoFormat()

if __name__ == "__main__": main()
