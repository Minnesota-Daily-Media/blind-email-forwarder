from __future__ import print_function
import pickle
import os.path
import base64
import email
import re
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def GetMessage(service, msg_id):
    message = service.users().messages().get(userId='me', id=msg_id).execute()

    headers = message['payload']['headers']

    to_email = [i['value'] for i in headers if i['name']=='To']

    parsed_email = re.split('@', to_email)

    if(parsed_email[1] == 'feedback.mndaily.com'):
        pass
        #lookup and Forward
    elif(parsed_email[0] == 'feedback' and parsed_email[1] == 'mndaily.com'):
        pass
        #create a alias and forward to gm@mndaily.com

    #print('To: %s' % to_email[0])

    '''
    message_parts = message['payload']['parts']
    part_one = message_parts[0]
    part_body = part_one['body']
    part_data = part_body['data']
    clean_one = part_data.replace("-","+")
    clean_one = clean_one.replace("_","/")
    clean_two = base64.b64decode(bytes(clean_one, 'UTF-8'))
    soup = BeautifulSoup(clean_two, "lxml")
    message_body = soup.body()
    body_message = '';
    '''

    message_raw = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()

    msg_str = base64.urlsafe_b64decode(message_raw['raw'].encode('UTF-8'))
    mime_msg = email.message_from_bytes(msg_str)

    #for part in mime_msg.walk():
    #    if(part.get_content_type() == 'text/html'):
    #        body_message = part

    #print(type(body_message))
    #print(str(body_message))
    #print(mime_msg.get_payload(1))
    body_message = mime_msg.get_payload(1).get_payload(decode=True)

    body_message = str(body_message)
    body_message = body_message[2:]
    #print(mime_msg)

    #print("Message body: %s" % message_body)

    #for p_tag in soup.find_all('p'):
    #    #print(p_tag.text, p_tag.next_sibling)
    #    body_message = body_message + p_tag.text

    SendMessage(service, body_message, 'nknudsen@mndaily.com', 'feedback@mndaily.com', 'Test Forward Message')

def SendMessage(service, payloadBody, toAddress, fromAddress, subject):
    message = MIMEText(payloadBody, 'html')
    message['to'] = toAddress
    message['from'] = fromAddress
    message['subject'] = subject

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
