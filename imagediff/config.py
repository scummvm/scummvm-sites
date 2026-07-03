import os
from dotenv import load_dotenv

load_dotenv()

SCREENSHOTS_DIR = os.environ.get("SCREENSHOTS_DIR", "./screenshots/")
CACHE_DIR = os.environ.get("CACHE_DIR", "./cache/")
