# libraries
from time import sleep, time
from pprint import pprint
from datetime import date
import os
import re
import requests

# local import of fbchat
from fbchat import Client
from fbchat.models import *

# maintain an exception list
exCeptionList = ['100013630894853']
grpList = []

# Subclass fbchat.Client and override required methods
class FbBot(Client):
   
    def __init__(self, *args, **kwargs):
       super().__init__(*args, **kwargs)
       self.messages = list()

    def onMessageUnsent(
        self,
        mid=None,
        author_id=None,
        thread_id=None,
        thread_type=None,
        ts=None,
        msg=None,
    ):
        for message in self.messages:
            if message.uid == mid:
                files, unsendable_files, shares = [], [], []
                for a in message.attachments:
                    print(a)
                    if isinstance(a, ImageAttachment):
                        if a.is_animated:
                            files.append(a.animated_preview_url)
                        else:
                            url = a.large_preview_url or a.preview_url or a.thumbnail_url
                            if url:
                                files.append(url)
                    elif isinstance(a, VideoAttachment):
                        files.append(a.preview_url)
                    elif isinstance(a, AudioAttachment):
                        fileName = a.filename[:-1]+'3'
                        r = requests.get(a.url)
                        with open(fileName, 'wb') as f:
                            f.write(r.content)
                        unsendable_files.append(fileName)
                    elif isinstance(a, FileAttachment):
                        r = requests.get(a.url)
                        url = re.search(
                            r"document\.location\.replace\(\"(.*)\"\);", r.text).group(1)
                        url = url.replace(r'\/', '/')
                        files.append(url)
                    elif isinstance(a, ShareAttachment):
                        shares.append([a.title, a.original_url, a.description])

                author = self.fetchUserInfo(message.author)[message.author]
                message.reply_to_id = None

                text = "{} deleted this message:".format(author.name)
                if message.sticker:
                    self.send(Message(text), thread_id, thread_type)
                    self.send(message, thread_id, thread_type)
                if message.text:
                    text = text+'\n\n'+message.text
                textMsz = Message(text, mentions=[Mention(
                    author.uid, length=len(author.name))])

                if unsendable_files or files or shares:
                    if unsendable_files:
                        self.sendLocalFiles(
                            unsendable_files, textMsz, thread_id, thread_type)
                    if files:
                        self.sendRemoteFiles(
                            files, textMsz, thread_id, thread_type)
                    if shares:
                        for share in shares:
                            self.send(Message('{} deleted a shared link:\n\n{}Link: {}\n\nDescription: {}'.format(
                                author.name, 'Title: '+share[0]+'\n\n' if share[0] != '' else '', share[1], share[2]),  mentions=[Mention(author.uid, length=len(author.name))]), thread_id, thread_type)
                else:
                    self.send(textMsz, thread_id, thread_type)

                self.messages = list(
                    filter(lambda x: x is not message, self.messages))
                for f in unsendable_files:
                    os.remove(f)
                #print(os.listdir())
                break

    # Override On Message Function of Class Client of fbchat Module
    def onMessage(
            self,
            mid=None,
            author_id=None,
            message=None,
            message_object=None,
            thread_id=None,
            thread_type=ThreadType.USER,
            ts=None, metadata=None, msg=None):

        if author_id != self.uid and author_id not in exCeptionList and (thread_type == ThreadType.USER or (thread_type == ThreadType.GROUP and thread_id in grpList)):
            message_object.uid = mid
            self.messages.append(message_object)
            for message in self.messages:
                ts = (time() - 10 * 60) * 1000
                if message.timestamp < ts:
                    self.messages = list(
                        filter(lambda x: x is not message, self.messages))

