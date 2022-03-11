import json

from mailto import mailto
from iNetToMailtoFormat import iNetToMailtoFormat
from iNettoMailto import iNettoMailto

EMAIL_DATA_JSON_FILE = "emaildata_v2.json"

# description:  will sort the file "emaildata_v2.json" email list such that it will
#               be easier to perform comparisons with using diff/meld or beyond compare

# note: this will overwrite the exisiting file. 

class emaildata_v2json_sort: 

    def __init__(self, fname): 
        self.fname = fname
        self.data = mailto.ReadJSONfile(self, self.fname) 

        for k,v in self.data.items():
            self.data[k] = sorted(v)

        print(json.dumps(self.data, sort_keys=True, indent=4, separators=(',',':')))

        iNettoMailto.WriteDatatoFile(self, self.data, self.fname)

def main():
    app = emaildata_v2json_sort(EMAIL_DATA_JSON_FILE)

if __name__ == "__main__": main()