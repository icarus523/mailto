import json
import os, sys
import hashlib
import re

from mailto import mailto

MAXIMUM_BLOCKSIZE_TO_READ = 65535
EMAIL_ADDRESS_REGEX = "\A[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\z"


class iNettoMailto: 

    def __init__(self, fname):
        self.filename = fname
        # Generate the Loookup File for Hashes : Email Addresses
        self.json_data = mailto.ReadJSONfile(self, self.filename) 
        self.email_address_hashed = self.ProcessEmailGroups(self.json_data)
        print(json.dumps(self.email_address_hashed, sort_keys=True, indent=4, separators=(',',':'))) # write to disk. 
        self.WriteDatatoFile(self.email_address_hashed, "sample_emaildata_lookup.json")
        
        # Converts emaildata.json to replace email addresses with Hashes
        self.emailgroups_data_w_hash = self.ConvertEmailData(self.json_data, self.email_address_hashed) 
        print(json.dumps(self.emailgroups_data_w_hash, sort_keys=True, indent=4, separators=(',',':'))) # write to disk.         
        self.WriteDatatoFile(self.emailgroups_data_w_hash, "sample_emaildata_v2.json")

        # Test Retrieves email address for the following email group. 
        test_mail_group = "OLGR Casino Inspectorate - Star Casino - Brisbane" 
        print(self.GetEmailAddressListString_from_EmailGroup(test_mail_group))
    
    def GetEmailAddressListString_from_EmailGroup(self, email_group_str): 
        email_hashes = self.emailgroups_data_w_hash[email_group_str]
        email_addresses = list() 
        for h in email_hashes: 
            email_addresses.append(self.email_address_hashed[h]) 
        
        return ";".join(email_addresses)
      
    def ProcessEmailGroups(self, jd): 
        email_address_dict = dict()
        for _,email_list in jd.items(): 
            for eaddr in email_list:              
                
                # string ';' in email address
                eaddr = re.sub(';', '', eaddr.lower())                
                # filter out just email address
                match = re.findall(r'[\w\.-]+@[\w\.-]+', eaddr) 

                hash_str = self.HashStr(match[0]) # hash the matched string            
                email_address_dict[hash_str] = match[0] # update
            
        # print(json.dumps(email_address_dict, sort_keys=True, indent=4, separators=(',',':'))) # write to disk. 
        return(email_address_dict) 

        
    def ReadJSONfile(self, json_filename):
        data = ''
        if (os.path.isfile(json_filename)): 
            with open(json_filename, 'r') as json_file:
                data = json.load(json_file)
        else:
            print(json_filename + " cannot be found.")
            sys.exit(2) # exit out cleanly. 
        
        return (data)

    def WriteDatatoFile(self, data, fname):
        with open(fname,'w+') as json_file:
            json.dump(data, json_file, sort_keys=True, indent=4, separators=(',',':'))
        # messagebox.showinfo("Backup Complete", "Backup of " + self.filename + ", has been saved as: " + output_backup_fname)

    def ConvertEmailData(self, email_data, email_hash_data):
        new_email_data = dict() 
        
        for email_group, email_list in email_data.items(): 
            email_hash_list = list()
            for email in email_list: 
                # string ';' in email address
                email = re.sub(';', '', email.lower())
                
                # filter out just email address
                match = re.findall(r'[\w\.-]+@[\w\.-]+', email) 
                
                if len(match) > 0: 
                    for hash, hashed_email in email_hash_data.items(): 
                        if hashed_email == match[0]: 
                            email_hash_list.append(hash) 
            
                    new_email_data[email_group] = sorted(email_hash_list)

        # print(json.dumps(new_email_data, sort_keys=True, indent=4, separators=(',',':'))) # write to disk. 
        return new_email_data
        
    def HashStr(self, s): 
        hash_obj = hashlib.sha256(str(s).encode('utf-8'))        
        return hash_obj.hexdigest()
        

def main():
    app = iNettoMailto("sample.json")

if __name__ == "__main__": main()
