import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())

from translation_provider import GoogleTranslateProvider, DeepLProvider

print("Testing Translation Provider Availability:")

print("\n--- Testing Google Translate Provider ---")
google = GoogleTranslateProvider()
print(f"Available: {google.available}")
if google.available:
    print(f"Provider: {getattr(google, 'provider', 'Unknown')}")
    try:
        print("Testing Translation: 'Hello'")
        result = google.translate("Hello")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Google Translate Provider is NOT available. Check dependencies (googletrans, google-cloud-translate, google-generativeai).")

print("\n--- Testing DeepL Provider ---")
deepl = DeepLProvider()
print(f"Available: {deepl.available}")
if deepl.available:
    try:
        print("Testing Translation: 'Hello'")
        result = deepl.translate("Hello")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("DeepL Provider is NOT available. Check DEEPL_API_KEY and dependencies.")
