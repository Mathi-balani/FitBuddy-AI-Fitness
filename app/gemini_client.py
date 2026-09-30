import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY and API_KEY.strip() == "PASTE_YOUR_GEMINI_API_KEY_HERE":
    API_KEY = None

FITNESS_MODEL = os.getenv("FITNESS_MODEL", "gemini-3.8-flash")
TIP_MODEL = os.getenv("TIP_MODEL", "gemini-3.8-flash")

client = genai.Client(api_key=API_KEY) if API_KEY else None
