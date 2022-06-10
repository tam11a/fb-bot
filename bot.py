
# library input
import os
from dotenv import load_dotenv
load_dotenv()

# third party library
import pyotp

# local import
from fbbot import FbBot


# Subclass fbchat.Client and override required methods
class Bot(FbBot):
    def on2FACode(self):
        if os.getenv('KEY'):
            return pyotp.TOTP(os.getenv('KEY')).now()
        else:
            return input('2FA Code --> ')