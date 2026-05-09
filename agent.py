import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from tools import get_pdf_metadata, apply_pdf_edits, replace_text_in_pdf

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY environment variable not set in .env. Using dummy key, API calls will fail.")
    api_key = "DUMMY_KEY"
    
client = genai.Client(api_key=api_key)

def run_agent(prompt: str, filepath: str) -> str:
    """Runs the ReAct loop using Gemini to edit the PDF."""
    print(f"Starting agent with file: {filepath}")
    
    full_prompt = f"Target PDF File: {filepath}\nUser Request: {prompt}\n\nPlease use the available tools to inspect the PDF and apply the requested edits."
    
    try:
        chat = client.chats.create(
            model='gemini-2.5-flash',
            config=types.GenerateContentConfig(
                temperature=0,
                tools=[get_pdf_metadata, apply_pdf_edits, replace_text_in_pdf],
            )
        )
        response = chat.send_message(full_prompt)
        return response.text
    except Exception as e:
        return f"Agent error: {str(e)}"

