import json
from mailto import mailto
from iNettoMailto import iNettoMailto

class DecodeMailtoGroups: 

    def __init__(self, fname, fname2):
        self.fname = fname
        self.fname_lookup = fname2

        # read encoded data
        data = mailto.ReadJSONfile(self, self.fname)

        # sort
        for k,v in data.items():
            data[k] = sorted(v)

        # read look-up data
        lookup_d = mailto.ReadJSONfile(self, self.fname_lookup)

        # decode data
        self.data_orig = self.DecodeEmailData(data, lookup_d)
        print(json.dumps(self.data_orig, sort_keys=True, indent=4, separators=(',',':'))) # write to disk.         

        iNettoMailto.WriteDatatoFile(self, self.data_orig, "sample_decoded_emaildata_v2.json")

    def DecodeEmailData(self, emaiL_data, lookup):
        new_email_data = dict() 
        
        for email_group, hashed_email_list in emaiL_data.items(): 
            email_list = list()
            for entry in hashed_email_list: 
                for email_hash, email in lookup.items(): 
                    if email_hash == entry:  
                        email_list.append(email.strip())

                new_email_data[email_group] = sorted(email_list)

        return new_email_data                        

def main():
    # input files are what is used in the mailto.py script
    app = DecodeMailtoGroups('emaildata_v2.json', 'emaildata_lookup.json')

if __name__ == "__main__": main()
