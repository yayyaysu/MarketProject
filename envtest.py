import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
bubble_api_token = os.getenv("BUBBLE_API_TOKEN")

# Print the environment variables
print(f"OPENAI_API_KEY: {openai_api_key}")
print(f"BUBBLE_API_TOKEN: {bubble_api_token}")

# Check if both variables were loaded successfully
if openai_api_key and bubble_api_token:
    print("✅ Successfully loaded both environment variables!")
else:
    print("❌ Failed to load one or both environment variables.")
    if not openai_api_key:
        print("  - OPENAI_API_KEY is missing")
    if not bubble_api_token:
        print("  - BUBBLE_API_TOKEN is missing")