# mailto.py
Script for handling Email Groups via JSON objects while utilising custom user email templates. 

An internal request to handle email groups that currently isn't supported by OLGR's current mail system.  
Glorified mailto: URI link handler  
This script has two utility script: 
* MailtoManage.py - Main utility to manage email groups. 
* TemplateEditor.py - Utility to generate Email Templates for used with the mailto.py script.  

mailto.py script uses templates generated by users to easily select functions to email to clients. The mail group database is stored as a JSON file. 

## How to Use

You just double-click the mailto.py file and provided your Operating System is configured to launch python scripts a GUI will be presented to you. 

Follow the "Quick HOWTO" instructions described above the screen.  

The "tabs": "EGM", "Systems" and "Other" represents the workflow of email templates Note: The "Other" tab is for email templates, which doesn't fit with either EGM/Systems. 
i.e. the addressee isn't exactly a client. 

## Creating new "Templates"

Best way of creating a template is to copy a new one, and replace the contents with 
the appropriate changes. 

## Restrictions with Creating New Templates
    1. The first word of the file name, will indicate where the template can be used. 
        e.g."EGM - Game Approval Letter.json" - will only be available in the "EGM"-tab. 
        Likewise, "Other - Technical Requirements" - will only be available in the "Other"-tab. 

    2.  Email addresses to be used in the "to:", "cc:" and "bcc:" sections should be 
        email groups that are available in the "emaildata.json" file. You can't put "bob@hotmail.com" 
        in the actual template. The Email: bob@hotmail.com can be added to any group listed
        in the "emaildata.json" file, and you would add that group to the template instead. 

    3.  BCC for EGM templates will be ignored, as TU doesn't bcc: anyone for any EGM related matters. 
        If there is a need to use bcc:, suggest to create an "OTHER"-type template instead. 
        
    4. Templates must be saved in the "templates" subdirectory. 
    
    5. Must utilise the following JSON structure: 

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


## Managing Email Group (Adding/Removing to exisiting Email Groups):

Use the built in tool for "Manage Group Emails" or edit the file: emaildata.json directly. 

## Adding a New Email Group. 

Use the Manage Email group function, and just create a new "Group Name" and add email addresses directly. 
These can now be accessed with the "OTHER" tab templates. The "new groups created will be
accessed dynamically. 
