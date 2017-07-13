from __future__ import print_function

import base64
from email.mime.text import MIMEText

import httplib2
import os

from apiclient import discovery
from googleapiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


# 获取Credentials，获得访问权限
def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


# 创建一个Message
def create_message(sender, to, subject, message_text):
    create_message_field = MIMEText(message_text)
    create_message_field['to'] = to
    create_message_field['from'] = sender
    create_message_field['subject'] = subject

    raw = base64.urlsafe_b64encode(create_message_field.as_bytes())
    raw = raw.decode()
    body = {'raw': raw}

    return body


# 发送一个Message
def send_message(to, subject, message_text):

    sender = 'enzo.kuang@shopeemobile.com'
    # to = "enzolife@foxmail.com"
    # subject = "Test Email"
    # message_text = '123'
    user_id = "enzo.kuang@shopeemobile.com"

    message = create_message(sender, to, subject, message_text)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    to = 'enzolife@foxmail.com'
    subject = 'test email'
    message_text = 'test message'

    send_message(to, subject, message_text)
