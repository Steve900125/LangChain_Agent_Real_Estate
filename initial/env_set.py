# File: manage_api_keys.py

from dotenv import load_dotenv, set_key
from pathlib import Path
import getpass
import os

# Specify the path to the .env file
env_path = Path('.env')

# Load environment variables from the .env file
load_dotenv(dotenv_path=env_path)

def check_and_set_api_key(key_name):
    """
    Check if the API key is set in the environment variables. 
    If not, prompt the user to enter it and save it to the .env file.
    """
    api_key = os.getenv(key_name)

    # If the API key doesn't exist, prompt the user to input it
    if not api_key:
        api_key = getpass.getpass(f"Please input your {key_name.replace('_', ' ')}:\n")
        os.environ[key_name] = api_key

        # Save the API key to the .env file for future use
        set_key(env_path, key_name, api_key)
        print(f"{key_name} has been set and saved to .env.")
    else:
        print(f"{key_name} already exists.")

def check_all_api_keys():
    """
    Check and ensure all required API keys are set.
    """
    api_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY"]
    
    for key in api_keys:
        check_and_set_api_key(key)

if __name__ == '__main__':
    check_all_api_keys()
