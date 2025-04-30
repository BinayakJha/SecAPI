# secapi/secure.py (Updated with password caching and hidden input only)

import json
import os
import base64
from getpass import getpass
from cryptography.fernet import Fernet

VAULT_PATH = os.path.expanduser("~/.secapi_vault.json")

_fernet_instance = None  # Cache for the Fernet object

def safe_input(prompt_text):
    """
    Always use hidden input for secrets.
    """
    return getpass(f"{prompt_text}: ")

def get_fernet():
    global _fernet_instance
    if _fernet_instance is None:
        password = safe_input("🔐 Enter your vault password")
        key = password.ljust(32, '0').encode()[:32]
        _fernet_instance = Fernet(base64.urlsafe_b64encode(key))
    return _fernet_instance

def add_key_interactively():
    print("\n🆕 Add a New API Key")
    key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()
    key_value = safe_input("🔑 Enter your API key").strip()

    if not key_name or not key_value:
        print("❌ Key name and value cannot be empty.")
        return

    fernet = get_fernet()
    encrypted = fernet.encrypt(key_value.encode()).decode()

    if os.path.exists(VAULT_PATH):
        with open(VAULT_PATH, 'r') as v:
            vault = json.load(v)
    else:
        vault = {}

    if key_name in vault:
        print(f"⚠️ Key '{key_name}' already exists. Overwriting...")

    vault[key_name] = encrypted
    with open(VAULT_PATH, 'w') as v:
        json.dump(vault, v, indent=2)

    print(f"✅ Key '{key_name}' securely stored in your vault.")
    print("\n🔁 Use it in your code like this:")
    print(f"    {key_name} = load_key(\"{key_name}\")\n")

def load_key(key_name):
    if not os.path.exists(VAULT_PATH):
        raise FileNotFoundError("Vault not found. Please run the CLI fixer first.")

    with open(VAULT_PATH, 'r') as v:
        vault = json.load(v)

    if key_name not in vault:
        raise KeyError(f"Key '{key_name}' not found in the vault.")

    fernet = get_fernet()
    encrypted = vault[key_name]
    decrypted = fernet.decrypt(encrypted.encode()).decode()
    return decrypted

def list_keys():
    if not os.path.exists(VAULT_PATH):
        print("🔒 No keys stored yet.")
        return

    with open(VAULT_PATH, 'r') as f:
        vault = json.load(f)

    if not vault:
        print("🔒 No keys stored yet.")
        return

    print("🔐 Stored Keys:")
    for key in vault:
        print(f"- {key}")

def delete_key(key_name):
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    with open(VAULT_PATH, 'r') as f:
        vault = json.load(f)

    if key_name in vault:
        del vault[key_name]
        with open(VAULT_PATH, 'w') as f:
            json.dump(vault, f, indent=2)
        print(f"🗑️ Key '{key_name}' deleted successfully.")
    else:
        print(f"❌ Key '{key_name}' not found in the vault.")

def rotate_key(key_name):
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    with open(VAULT_PATH, 'r') as f:
        vault = json.load(f)

    if key_name not in vault:
        print(f"❌ Key '{key_name}' not found in the vault.")
        return

    new_value = safe_input(f"🔁 Enter new value for key '{key_name}'").strip()
    fernet = get_fernet()
    encrypted = fernet.encrypt(new_value.encode()).decode()
    vault[key_name] = encrypted
    with open(VAULT_PATH, 'w') as f:
        json.dump(vault, f, indent=2)
    print(f"🔁 Key '{key_name}' rotated successfully.")