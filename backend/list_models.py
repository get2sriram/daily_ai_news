import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file.")
else:
    genai.configure(api_key=api_key)
    
    print(f"Listing models available for your API key...")
    print("-" * 50)
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model: {m.name}")
                print(f"Display Name: {m.display_name}")
                print(f"Supported Methods: {m.supported_generation_methods}")
                print("-" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")
