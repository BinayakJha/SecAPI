
# demo_projects/example.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from secapi.secure import load_key



# Simulated hardcoded API keys
openai_key = load_key("openai_key")
github_keys = load_key("github_keys")
some_variable = "this is not a key"

# Simulated function that uses the keys
def my_function():
    # Use the keys in your code
    openai_api_key = openai_key
    github_api_keys = github_keys

    # Do something with the keys
    print("Using OpenAI API key:", openai_api_key)
    print("Using GitHub API keys:", github_api_keys)

    # Do something else
    print("Some other code...")

    # Use the keys in another function
    another_function(github_api_keys)



def another_function(github_api_keys):
    # Use the keys in another function
    print("Using GitHub API keys in another function:", github_api_keys)

    # Do something else
    print("Some other code in another function...")

    # 


if __name__ == "__main__":
    my_function()
    another_function(github_keys)