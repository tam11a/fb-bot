# library input
import os
from dotenv import load_dotenv
load_dotenv()

# local import
from bot import Bot

client = Bot(os.getenv('EMAIL'), os.getenv('PASSWORD'))
client.listen()