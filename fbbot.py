# local import of fbchat
from fbchat import Client

# Subclass fbchat.Client and override required methods
class FbBot(Client):
   
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        # If you're not the author, echo
        if author_id != self.uid:
            print(message_object.text)
            self.send(message_object, thread_id=thread_id, thread_type=thread_type)

