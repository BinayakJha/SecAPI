# Handles encryption and replacement
from sentinel.secure import load_key
import os
import re
import json
from getpass import getpass
from cryptography.fernet import Fernet
import base64

VAULT_PATH = os.path.expanduser("~/.sentinelai_vault.json")

def get_fernet():
    """
    Prompts the user for a password to access the vault and generates a Fernet
    encryption object. The password is padded to 32 bytes and encoded to create 
    a base64 URL-safe encryption key.
    """
    password = getpass("🔐 Enter your password to access the vault: ")
    key = password.ljust(32, '0').encode()[:32]
    return Fernet(base64.urlsafe_b64encode(key))



def suggest_and_fix(file, line_num, line_content, label):
    print("💡 Suggestion: This looks like a hardcoded " + label + " key.")
    print("Options:")
    print("  [1] Replace with secure reference")
    print("  [2] Store in encrypted vault")
    print("  [3] Ignore")
    choice = input("Select an option: ").strip()

    if choice == "1" or choice == "2":
        f = get_fernet()
        key_match = re.search(r'"(.*?)"', line_content)
        if key_match:
            secret = key_match.group(1)
            encrypted = f.encrypt(secret.encode()).decode()
            key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()
            
            # Update the file
            with open(file, 'r') as f_in:
                lines = f_in.readlines()
            new_line = f"{key_name} = load_key(\"{key_name}\")\n"
            lines[line_num - 1] = new_line
            with open(file, 'w') as f_out:
                f_out.writelines(lines)

            # Save to vault
            if os.path.exists(VAULT_PATH):
                with open(VAULT_PATH, 'r') as v:
                    vault = json.load(v)
            else:
                vault = {}

            vault[key_name] = encrypted
            with open(VAULT_PATH, 'w') as v:
                json.dump(vault, v, indent=2)

            print(f"✅ Key '{key_name}' securely stored and replaced in file.")
    else:
        print("⚠️  Skipped.")