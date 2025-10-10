import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    PORT = int(os.getenv("PORT", 5003))
