import google.generativeai as genai
import os

# Paste your key here again just for this test
GOOGLE_API_KEY = "AIzaSyBpCmciF5FnodheLTZIssgsCzFy_ZIOxf4"
genai.configure(api_key=GOOGLE_API_KEY)

print("🔍 Checking available models...")
try:
    for m in genai.list_models():
        # Only show models that generate text
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ Found: {m.name}")
except Exception as e:
    print(f"❌ Error: {e}")