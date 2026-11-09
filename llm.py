# all the gemini code lives here so it can be swapped for another llm later
# (e.g. ollama for offline use) without touching the rest of the project
import os

from dotenv import load_dotenv
from google import genai

# reads the .env file and loads GEMINI_API_KEY into the environment
load_dotenv()

# model name kept in one place so its easy to change
# check google ai studio for the current free model names
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

# creates the gemini client using the key from .env
# os.getenv returns None if the key is missing, so we check for that first
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing - check your .env file")

client = genai.Client(api_key=api_key)


# sends a prompt to gemini and returns the reply as plain text
def ask_llm(prompt):
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


# quick test - only runs when you do "python llm.py", not when imported
if __name__ == "__main__":
    print(ask_llm("Reply with the word OK and nothing else."))