# secapi/secure.py (Password-required key deletion)

import json
import os
import base64
from getpass import getpass
from cryptography.fernet import Fernet

VAULT_PATH = os.path.expanduser("~/.secapi_vault.json")

_fernet_instance = None  # Global cached Fernet

def safe_input(prompt_text):
    return getpass(f"{prompt_text}: ")

def get_fernet():
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    password = safe_input("🔐 Enter your master vault password")
    key = base64.urlsafe_b64encode(password.ljust(32, '0').encode()[:32])
    f = Fernet(key)

    if os.path.exists(VAULT_PATH):
        try:
            with open(VAULT_PATH, 'r') as v:
                vault = json.load(v)
            if vault:
                test_value = next(iter(vault.values()))
                f.decrypt(test_value.encode())  # Validate password
        except Exception:
            print("❌ Invalid password for the current vault.")
            exit(1)

    _fernet_instance = f
    return _fernet_instance

def change_vault_password():
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    try:
        old_fernet = get_fernet()
        with open(VAULT_PATH, 'r') as f:
            vault = json.load(f)

        decrypted = {k: old_fernet.decrypt(v.encode()).decode() for k, v in vault.items()}

        new_pass = getpass("🔐 Enter your new master password: ")
        confirm = getpass("🔁 Confirm new password: ")
        if new_pass != confirm:
            print("❌ Passwords do not match.")
            return

        new_key = base64.urlsafe_b64encode(new_pass.ljust(32, '0').encode()[:32])
        new_fernet = Fernet(new_key)

        new_vault = {k: new_fernet.encrypt(v.encode()).decode() for k, v in decrypted.items()}

        with open(VAULT_PATH, 'w') as f:
            json.dump(new_vault, f, indent=2)

        print("✅ Vault password updated successfully.")

    except Exception as e:
        print(f"❌ Failed to change password: {e}")

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

    fernet = get_fernet()  # 🔐 Require password before deletion

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
