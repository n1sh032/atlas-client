
# just the gemini client setup, in its own file since a few other files need it
# and i didnt want circular import issues

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))