# Handles encryption and replacement
import os
import re
import json
import base64
from getpass import getpass
from cryptography.fernet import Fernet
from secapi.secure import load_key

VAULT_PATH = os.path.expanduser("~/.secapi_vault.json")


def get_fernet():
    """
    Prompts the user for a password to access the vault and generates a Fernet
    encryption object. The password is padded to 32 bytes and encoded to create
    a base64 URL-safe encryption key.
    """
    try:
        password = getpass("🔐 Enter your password to access the vault: ")
        key = password.ljust(32, '0').encode()[:32]
        return Fernet(base64.urlsafe_b64encode(key))
    except Exception as e:
        print(f"❌ Failed to generate encryption key: {e}")
        raise


def update_file(file, line_num, key_name):
    """
    Updates the specified line in the file to replace the hardcoded secret
    with a secure reference using `load_key()`.
    """
    try:
        with open(file, 'r') as f_in:
            lines = f_in.readlines()

        new_line = f"{key_name} = load_key(\"{key_name}\")\n"
        lines[line_num - 1] = new_line

        with open(file, 'w') as f_out:
            f_out.writelines(lines)

        print(f"✅ Updated file '{file}' to use secure reference for '{key_name}'.")
    except Exception as e:
        print(f"❌ Failed to update file '{file}': {e}")
        raise


def update_vault(key_name, encrypted):
    """
    Updates the vault with the new encrypted secret.
    """
    try:
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, 'r') as v:
                vault = json.load(v)
        else:
            vault = {}

        vault[key_name] = encrypted

        with open(VAULT_PATH, 'w') as v:
            json.dump(vault, v, indent=2)

        print(f"✅ Key '{key_name}' securely stored in the vault.")
    except Exception as e:
        print(f"❌ Failed to update vault: {e}")
        raise


def suggest_and_fix(file, line_num, line_content, label):
    """
    Suggests and applies fixes for hardcoded secrets detected in the file.
    """
    print(f"💡 Suggestion: This looks like a hardcoded {label} key.")
    print("Options:")
    print("  [1] Replace with secure reference")
    print("  [2] Store in encrypted vault")
    print("  [3] Ignore")
    choice = input("Select an option: ").strip()

    if choice in {"1", "2"}:
        try:
            fernet = get_fernet()
            key_match = re.search(r'"(.*?)"', line_content)
            if key_match:
                secret = key_match.group(1)
                encrypted = fernet.encrypt(secret.encode()).decode()
                key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()

                # Update the file and vault
                update_file(file, line_num, key_name)
                update_vault(key_name, encrypted)
            else:
                print("❌ No valid secret found in the line.")
        except Exception as e:
            print(f"❌ Failed to process the secret: {e}")
    elif choice == "3":
        print("⚠️  Skipped.")
    else:
        print("❌ Invalid choice. Skipping.")