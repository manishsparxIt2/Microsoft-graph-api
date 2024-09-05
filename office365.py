import requests
from sqlalchemy import create_engine ,text

from config  import *
import base64
import re
from fuzzywuzzy import fuzz


class office365():
    def __init__(self):        
    # Constants - Replace these with your own values
        self.tenant_id = 'xxxxxxxxxxxxxxxx'
        self.client_id = 'XxxxxxxxXxxxxxxxxxxxxxxxxxxxxx'
        self.client_secret = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        self.user_id = 'info@myvehicle.in'
# Authentication endpoint for obtaining the access token
        self.token_url = f'https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token'

# Requesting an access token
        self.token_data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://graph.microsoft.com/.default'
        }


    def db_connect(self):
        engine = create_engine(DB_CONNECT ,pool_size=30,max_overflow=30)    
        return engine


    # Get the token

    def gettoken(self):
        token_response = requests.post(self.token_url, data=self.token_data)
        token_response_json = token_response.json()
    # Extract the access token from the response
        access_token = token_response_json.get('access_token')
        return access_token

#print(access_token)

    def getallUser(self):

        userid = list()

        if self.gettoken():
            engine = self.db_connect()
            # Set up the request headers with the access token
            headers = {
                'Authorization': f'Bearer {self.gettoken()}',
                'Content-Type': 'application/json'
            }

            # Retrieve the list of users in the tenant
            users_url = 'https://graph.microsoft.com/v1.0/users'
            users_response = requests.get(users_url, headers=headers)

            #print(users_response.json())

            if users_response.status_code == 200:
                users = users_response.json().get('value', [])

                # Loop through the list of users and print their email addresses
               
                for user in users:
                    print(f"User: {user['displayName']}, Email: {user['mail']} ,ID {user['id']}" , "----------------------")

                    sql = "INSERT INTO o365.tbl_email_users ( user_office_id, user_email, user_name)   VALUES( '"+user['id']+"', '"+user['mail']+"', '"+user['displayName']+"') on conflict (user_office_id) do update set  user_name = '"+user['displayName']+"'"
                    #print(sql)
                    try:
                        with engine.connect() as connection:
                            connection.execute(text(sql))
                            connection.commit()
                    except Exception as e:
                        print(e)
                        #exit;
                    
                    userid.append(user['id'])
        return userid

#print(getallUser())

    def getAllemails(self):
        if self.gettoken():
            # Set up the request headers with the access token
            headers = {
                'Authorization': f'Bearer {self.gettoken()}',
                'Content-Type': 'application/json'
            }
            usersids =  self.getallUser()

            # Define the date from which you want to fetch emails
                #received_date = '2023-09-01T00:00:00Z'  # Format: YYYY-MM-DDTHH:MM:SSZ
                #    query_params = f'?$filter=receivedDateTime ge {received_date}'

                # Making the GET request to retrieve emails
                #response = requests.get(graph_api_url + query_params, headers=headers)
                   #fetch_emails('Inbox', received_date, 'receivedDateTime')    
            if usersids:
                
                for user_id in usersids: 
                    self.fetch_emails('Inbox' ,'' , '',user_id ,headers)
                    self.fetch_emails('SentItems' ,'' , '',user_id ,headers)        
                
                    
    # Function to fetch emails from a specified folder
    def fetch_emails(self,folder_id, date_filter, filter_type ,user_id ,headers):  
        engine = self.db_connect()             
        graph_api_url = f'https://graph.microsoft.com/v1.0/users/{user_id}/mailFolders/{folder_id}/messages'
        #query_params = f'?$filter={filter_type} ge {date_filter}'
        #response = requests.get(graph_api_url + query_params, headers=headers)
        response = requests.get(graph_api_url, headers=headers)
       
        sql = "";

        if response.status_code == 200:
            emails = response.json().get('value', [])
            #print(emails)
            #print("########"*50)
            if emails:
                for email in emails:                   
                    toemail = list()
                    for torecipient in email['toRecipients']:
                       toemail.append(torecipient['emailAddress']['name'] + " <" +torecipient['emailAddress']['address'] + " >" ) 
                    toemail =  (',').join(toemail) 
                    # print(f"Subject: {email['subject']}")
                    # print(f"To: {toemail}")
                    # print(f"From: {email['from']['emailAddress']['name']} <{email['from']['emailAddress']['address']}>")
                    # print(f"Received: {email['receivedDateTime']}")

                    # print(f"Body Preview: {email['bodyPreview']}")
                    # print("-" * 40)
                    # #print(f"Body: {email['body']['content']}")
                    # print("-" * 40)
                    fromemail =f"{email['from']['emailAddress']['name']} <{email['from']['emailAddress']['address']}>" 
                    highlight_keyword = self.highlight_text(email['body']['content'] , search_words)

                     
                    if 'is_flagged' in highlight_keyword:
                        if highlight_keyword['is_flagged']== 'YES':
                            print(highlight_keyword['email_body'])
                            keywords= ','.join(highlight_keyword['key_words'])
                        

                            sql  ="INSERT INTO o365.tbl_emails (is_flagged ,flagged_keywored, email_type, email_subject, email_from, email_to, email_id, run_date,  email_body, body_preview ) values ( 'YES', '"+keywords+"' , '"+folder_id+"' , '"+email['subject']+"' ,'"+fromemail+"','"+toemail+"', '"+email['id']+"' , current_date , '"+str(base64.b64encode(highlight_keyword['email_body'].encode()).decode('utf-8'))+"', '"+str(base64.b64encode(email['bodyPreview'].encode()).decode('utf-8'))+"' ) on conflict (email_id) do update set email_body = '"+str(base64.b64encode(highlight_keyword['email_body'].encode()).decode('utf-8'))+"' "

                            try:
                                with engine.connect() as connection:                                    
                                    connection.execute(text(sql))
                                    connection.commit()

                            except Exception as e:
                                print(e)
            else:
                print(f"No emails found in the {folder_id} folder for the specified date.")
        else:
            print(f"Failed to retrieve emails from {folder_id}: {response.status_code} {response.text}")

    
    def highlight_text(self ,email_body, search_word):
        result = dict()
        keyword = list()
        for text_to_find in search_word:
            #start_index = email_body.lower().find(text_to_find.lower())
            matches = re.finditer(text_to_find.lower(), email_body.lower())
            offset = 0
            #print(matches.start())
            highlighted_text = email_body
                           
                
                #end_index = start_index + len(text_to_find)
            for match in matches:
                result['is_flagged'] = 'YES'
                start, end = match.start() + offset, match.end() + offset
                highlighted_text = highlighted_text[:start] + "**" + highlighted_text[start:end] + "**" + highlighted_text[end:]
                offset += 4           
                keyword.append(text_to_find.lower())
            email_body = highlighted_text
        else:
            email_body =  email_body
        result['email_body'] = email_body
        result['key_words'] = list(set(keyword))
        return result

if __name__=="__main__":
    o365 =  office365()
    o365.getAllemails()