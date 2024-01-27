import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.environ.get("BOT_TOKEN")
channel_id = os.environ.get("CHANNEL_ID")
