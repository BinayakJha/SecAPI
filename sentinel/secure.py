import json
import os
from getpass import getpass
from cryptography.fernet import Fernet

VAULT_PATH = os.path.expanduser("~/.sentinelai_vault.json")

import base64

def get_fernet():
    password = getpass("🔐 Enter your password to access the vault: ")
    key = password.ljust(32, '0').encode()[:32]
    return Fernet(base64.urlsafe_b64encode(key))


def add_key_interactively():
    print("\n🆕 Add a New API Key")
    key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()
    key_value = getpass("Paste the value (it will be hidden): ").strip()

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

    f = get_fernet()
    encrypted = vault[key_name]
    decrypted = f.decrypt(encrypted.encode()).decode()
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

    new_value = getpass(f"🔁 Enter new value for key '{key_name}': ")
    f = get_fernet()
    encrypted = f.encrypt(new_value.encode()).decode()
    vault[key_name] = encrypted
    with open(VAULT_PATH, 'w') as f:
        json.dump(vault, f, indent=2)
    print(f"🔁 Key '{key_name}' rotated successfully.")
