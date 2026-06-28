import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

SCAN_INTERVAL_MINUTES = 60
STRONG_DCA_SCORE = 80
DCA_SCORE = 60
WATCH_SCORE = 40