from __future__ import print_function

import base64
from email.mime.text import MIMEText
from pprint import pprint

import httplib2
import os

from apiclient import discovery
from googleapiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import pandas as pd

import json

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
    sender = 'enzo.kuang@shopee.com'
    # to = "enzolife@foxmail.com"
    # subject = "Test Email"
    # message_text = '123'
    user_id = "enzo.kuang@shopee.com"

    message = create_message(sender, to, subject, message_text)

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        print('Email is sent.')
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# 搜索邮件，获取邮件ID
def ListMessagesMatchingQuery(user_id, query='', max_results=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.
        
        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
    """
    # 判断是否有max_results
    if max_results is None:
        try:
            response = service.users().messages().list(userId=user_id,
                                                       q=query).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = service.users().messages().list(userId=user_id, q=query,
                                                           pageToken=page_token).execute()
                messages.extend(response['messages'])

            return messages
        except errors.HttpError as error:
            print('An error occurred: %s' % error)
    else:
        try:
            response = service.users().messages().list(userId=user_id,
                                                       q=query,
                                                       maxResults=max_results).execute()
            messages = []
            if 'messages' in response:
                messages.extend(response['messages'])

            return messages
        except errors.HttpError as error:
            print('An error occurred: %s' % error)


# 获取邮件ID后，检索邮件正文
def GetMessage(user_id, msg_id):
    """Get a Message with given ID.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.
    
    Returns:
    A Message.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        print('Message snippet: %s' % message['snippet'])

        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# 从邮件正文中，检索附件ID
def GetAttachmentID(msg_id):
    # json转换
    json_str = json.dumps(GetMessage('me', msg_id))
    data = json.loads(json_str)
    # 通过json获取attachmentId
    attachmentId = data['payload']['parts'][1]['body']['attachmentId']
    return attachmentId


# 获得附件，转为Data Frame或下载
def GetAttachments(user_id, msg_id, store_dir, file_rename, data_frame=0):
    """Get and store attachment from Message with given id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    store_dir: The directory used to store attachments.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments() \
                        .get(userId=user_id, messageId=msg_id, id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = ''.join([store_dir, file_rename])

                f = open(path, 'wb')
                f.write(file_data)
                f.close()

                if data_frame == 1:
                    pwd = os.getcwd()  # 首先取初始工作目录
                    os.chdir(os.path.dirname(path))
                    attachment_data_frame = pd.read_csv(os.path.basename(path), index_col=None, header=0)
                    os.chdir(pwd)
                    return attachment_data_frame

    except errors.HttpError as error:
        print('An error occurred: %s' % error)


# 获得多个附件，转为Data Frame或下载
def GetMultiAttachments(user_id, msg_id, store_dir, file_rename, data_frame=0):
    """Get and store attachment from Message with given id.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: ID of Message containing attachment.
    store_dir: The directory used to store attachments.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()

        att_num = 0

        for part in message['payload']['parts']:
            if part['filename']:
                if 'data' in part['body']:
                    data = part['body']['data']
                else:
                    att_id = part['body']['attachmentId']
                    att = service.users().messages().attachments() \
                        .get(userId=user_id, messageId=msg_id, id=att_id).execute()
                    data = att['data']
                file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                path = ''.join([store_dir, file_rename[att_num]])

                f = open(path, 'wb')
                f.write(file_data)
                f.close()

                att_num = att_num + 1

        if data_frame != 0:
            pwd = os.getcwd()  # 首先取初始工作目录
            open_path = ''.join([store_dir, file_rename[data_frame - 1]])
            os.chdir(os.path.dirname(open_path))
            attachment_data_frame = pd.read_csv(os.path.basename(open_path), index_col=None, header=0)
            os.chdir(pwd)
            return attachment_data_frame

    except errors.HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':

    to = 'enzolife@foxmail.com'
    subject = 'test email'
    message_text = 'test message'

    send_message(to, subject, message_text)
    '''
    search_message = ListMessagesMatchingQuery('me',
                                               'from:(nanzheng.lin@shopee.com) Daily Sub-category Detailed Report',
                                               )
    search_message_filtered = search_message[0]['id']

    pprint(search_message)
    pprint(search_message_filtered)

    # pprint(GetMessage('me', '15f08a663a285a9e'))
    json_str = json.dumps(GetMessage('me', '15f08a663a285a9e'))
    data = json.loads(json_str)
    pprint(data)
    print(data['payload']['parts'][1]['body']['attachmentId'])
    
    print(GetMultiAttachments('me',
                              search_message_filtered,
                              'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2017.8.2 Local Stat\\',
                              ['Total_Local_CB_Cumulative_SKUs.csv', 'Total_Local_CB_30day_gross_orders.csv'],
                              1
                              ))
                              '''
