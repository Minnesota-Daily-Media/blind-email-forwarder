from __future__ import print_function
import pickle
import os.path
import base64
import email
import re
import mysql.connector
import json
import random
import string
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

with open("./mysql.json", "r") as handler:
    mysql_creds = json.load(handler)

mysql_user = mysql_creds["user"]
mysql_pass = mysql_creds["password"]

db = mysql.connector.connect(
    host="localhost",
    database="mndailyemailalias",
    user=mysql_user,
    passwd=mysql_pass
)

def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def GetMessage(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id).execute()

    headers = message['payload']['headers']

    to_email = [i['value'] for i in headers if i['name']=='To']
    from_email = [i['value'] for i in headers if i['name']=='From']

    parsed_to_email = re.split('@', str(to_email))

    if('feedback.mndaily.com' in parsed_to_email[1]):
        #lookup and forward
        alias = parsed_to_email[0][2:]
        print(alias)
    elif(("MNDaily Feedback" in parsed_to_email[0] or parsed_to_email[0] == 'feedback') and 'mndaily.com' in parsed_to_email[1]):
        #create a alias and forward to gm@mndaily.com
        alias = randomString()
        alias = alias + '@feedback.mndaily.com'

        print(alias)

        cursor = db.cursor()

        sql = "INSERT INTO emailalias (email, alias) VALUES (%s, %s)"
        val = (str(from_email), alias)
        cursor.execute(sql, val)

        db.commit()

        print(cursor.rowcount, "record inserted")


        message_raw = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()

        msg_str = base64.urlsafe_b64decode(message_raw['raw'].encode('UTF-8'))
        mime_msg = email.message_from_bytes(msg_str)

   
        body_message = mime_msg.get_payload(1).get_payload(decode=True)

        body_message = str(body_message)
        body_message = body_message[2:]
    

        SendMessage(service, body_message, 'nknudsen@mndaily.com', 'feedback@mndaily.com', alias, 'Feedback Received')

def SendMessage(service, payloadBody, toAddress, fromAddress, replyTo, subject):
    message = MIMEText(payloadBody, 'html')
    message['to'] = toAddress
    message['from'] = fromAddress
    message['subject'] = subject
    message.add_header('reply-to', replyTo)

    message_raw = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    message_send = service.users().messages().send(userId='me', body=message_raw).execute()

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    label_ids = ['UNREAD', 'INBOX']

    results = service.users().messages().list(userId='me', labelIds=label_ids).execute()
    messages = []

    if 'messages' in results:
        messages.extend(results['messages'])
    while 'nextPageToken' in results:
        page_token = results['nextPageToken']
        results = service.users().messages().list(userId='me', labelIds=label_ids).execute()

        messages.extend(results[messages])

    if not messages:
        print('No unread messages found.')
    else:
        for messageId in messages:
            GetMessage(service, messageId['id'])

if __name__ == '__main__':
    main()
