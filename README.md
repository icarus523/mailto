# mailto.py
Script for handling Email Groups via JSON objects while utilising custom user email templates. 

An internal request to handle email groups that currently isn't supported by OLGR's current mail system.  
Glorified mailto: URI link handler  
This script has three utility scripts: 
* MailtoManage.py - Main utility to manage email groups. 
* TemplateEditor.py - Utility to generate Email Templates for used with the mailto.py script.  
* mailtodata.py - Utility to convert previous `emaildata.json` to `emaildata_v2.json` and `emaildata_lookup.json` files

mailto.py script uses templates generated by users to easily select email templates with custom email groups to clients. The mail group database is stored as a JSON file. 

As of v0.6 the script has been updated to support unique email addresses. Email Groups will therefore be more accurate as only one email address exists for that user. This is accomplished via truncating the email address to just: `blah@domain.com` and generating a hash, and using a flat table with the hash as an index to the actual email address (refer `emaildata_lookup.json` for details) 

Hashing of Email Groups for added security has also been added to prevent unauthorised changes directly to the .json file. 

## How to Use

You just double-click the `mailto.pym` file and provided your Operating System is configured to launch python scripts a GUI will be presented to you. 

Otherwise in Windows type: 
````
py mailto.pym
````
Follow the "Quick HOWTO" instructions described above the screen.  

The "tabs": "EGM", "Systems" and "Other" represents the workflow of email templates Note: The "Other" tab is for email templates, which doesn't fit with either EGM/Systems. 
i.e. the addressee isn't exactly a client. 

## Creating new "Templates"

Best way of creating a template is to copy a new one, and replace the contents with 
the appropriate changes using the TemplateEditor.py script.  

Otherwise use the `TemplateEditor.py` script and design the template. This allows you to set email subject and body. 

## Restrictions with Creating New Templates
    1. The first word of the file name, will indicate where the template can be used. 
        e.g."EGM - Game Approval Letter.json" - will only be available in the "EGM"-tab. 
        Likewise, "Other - Technical Requirements" - will only be available in the "Other"-tab. 

    2.  Email addresses to be used in the "to:", "cc:" and "bcc:" sections should be 
        email groups that are available in the "emaildata_v2.json" file. You can't put "bob@hotmail.com" 
        in the actual template. The Email: bob@hotmail.com can be added to any group listed
        in the "emaildata.json" file, and you would add that group to the template instead. 
       
    3. Templates must be saved in the "templates" subdirectory. 
    
    4. Must utilise the following JSON structure: 

        {
          "$schema": "http://json-schema.org/draft-04/schema#",
          "type": "object",
          "properties": {
            "Email Template": {
              "type": "object",
              "properties": {
                "title": {
                  "type": "string"
                },
                "to": {
                  "type": "array",
                  "items": {
                        "type": "string"
                  }
                },
                "cc": {
                  "type": "array",
                  "items": {
                        "type": "string"
                  }
                },
                "bcc": {
                  "type": "array",
                  "items": {
                        "type": "string"
                  }
                },
                "subject": {
                  "type": "string"
                },
                "body": {
                  "type": "string"
                }
              },
              "required": [
                "title",
                "to",
                "cc",
              ]
            }
          }
        }


## Managing Email Group (Getting Password Access to Manage Email Groups):

For added security, the use of the `MailtoManage.py` is now password protected.  This is to ensure that only Authorised users are capable of changing details of an email group. To add a new authorised user (a new password): you will need to modify the `MailtoManage.py` script (i.e. source code) and add the result of the following `python3` code to the `VALID_PASSWORD` list variable: 

```
clear_text_password = "supersecret2018!"
your_password = hashlib.sha256(clear_text_password.encode()).hexdigest()
```
The output of the above code is to be appended to the following list: 

```
VALID_PASSWORDS = ["63f6a3533a1d65ea4cc016ef2371c09bce7a00b3d4495e2cf6eec18d4083e1f0", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]
```

This keeps honest people honest. 

Further more, the email database file (emaildata_v2.json), is also now signed for each email group. This prevents unauthorised changing of the email groups without triggering a warning that hashes doesn't match. E.g.
```
    {
        "Email Hash":"b613eb430b4ab3381439fbfd0e1936328083e7ae525910841598a88f95539e6b",
        "Email Group":"Jurisdiction NZ"
    },
    {
        "Email Hash":"169c894e2654c66766d00769e44609f4f4ac5f370a65f10c3fe14bdbf927ae37",
        "Email Group":"EGM SG Gaming"
    },
```

### Important: Do not attempt to edit any of the JSON files used, unless you know what you're doing as any errors will prevent the script from functioning correctly. This is the reason why hashing of email groups, email addresses and password restrictions has been implemented. 

## Adding a New Email Group. 

Use the `MailtoManage.py` script: 

* Enter a new "Group Name" in the DropDown Menu and add email addresses directly.
* Each email address must be on a separate line
* No commas, semi-colons, etc
* Click `Save Changes` and `Refresh` buttons

The newly created groups created will be accessed dynamically. 

Tips: If you want the email groups to be available in the EGM/Systems Tab window in the mailto.py script then pre-pend "EGM" or "SYSTEMS" respectively to the Email Group Name. 

## Removing an Exisiting Email Group

Use the MailtoManage.py script: 

* Select the Email Group you want to remove. 
* Press `Delete Email Group` button. 
* Press `Refresh` Button to confirm that the email group has been removed. 

## Maintaining Emails within Email Groups

If a person's email address is no longer being used (i.e. left their company), they should be removed using the MailtoManage.py script using the following method: 

Use the MailtoManage.py script to remove an Email Address: 

* Select the Email Group that the user exists in. 
* Remove email address from the Email Group 
* Click `Save Changes` and `Refresh` buttons
* Repeat for any other email groups the email address might be part of

Use the MailtoManage.py script to add an Email Address to an email group: 

* Select the Email Group that you want the user to be part of. 
* Add the email address into the Email Group, note that the script will strip out unnecessary strings of characters which do not form part of an email address in the following format: `username@domain`
* Click `Save Changes` and `Refresh` buttons
* Confirm that the addition of the email address has been made
