from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Access variables
api_key = os.getenv("API_KEY")
debug_mode = os.getenv("DEBUG")

print("API_KEY:", api_key)
print("DEBUG:", debug_mode)
