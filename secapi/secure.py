# secapi/secure.py (Password-required key deletion)

import json
import os
import base64
import secrets
import datetime
from getpass import getpass
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

VAULT_PATH = os.path.expanduser("~/.secapi_vault.json")
CURRENT_ENV = None

# Automatically set environment from OS env var if present
env_from_os = os.environ.get("SECAPI_ENV")
if env_from_os:
    CURRENT_ENV = env_from_os.lower().strip()
    VAULT_PATH = os.path.expanduser(f"~/.secapi_vault_{CURRENT_ENV}.json")

def set_current_env(env_name):
    global CURRENT_ENV, VAULT_PATH
    if env_name:
        CURRENT_ENV = env_name.lower().strip()
        VAULT_PATH = os.path.expanduser(f"~/.secapi_vault_{CURRENT_ENV}.json")
    else:
        CURRENT_ENV = None
        VAULT_PATH = os.path.expanduser("~/.secapi_vault.json")

_fernet_instance = None  # Global cached Fernet of the master key

def safe_input(prompt_text):
    return getpass(f"{prompt_text}: ")

def legacy_derive_key(password: str) -> bytes:
    """Old insecure key derivation using padding."""
    return base64.urlsafe_b64encode(password.ljust(32, '0').encode()[:32])

def derive_key(password: str, salt: bytes) -> bytes:
    """Secure key derivation using PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def generate_recovery_key() -> str:
    """Generate a 24-character hexadecimal formatted recovery key."""
    return '-'.join(secrets.token_hex(2).upper() for _ in range(6))

def _initialize_new_vault(password):
    """Initializes a new vault with a random master key and recovery key."""
    master_key = Fernet.generate_key()
    recovery_key = generate_recovery_key()

    salt = os.urandom(16)
    recovery_salt = os.urandom(16)

    pass_derived_key = derive_key(password, salt)
    rec_derived_key = derive_key(recovery_key, recovery_salt)

    f_pass = Fernet(pass_derived_key)
    f_rec = Fernet(rec_derived_key)

    enc_master_pass = f_pass.encrypt(master_key).decode()
    enc_master_rec = f_rec.encrypt(master_key).decode()

    vault_data = {
        "salt": base64.b64encode(salt).decode(),
        "recovery_salt": base64.b64encode(recovery_salt).decode(),
        "enc_master_pass": enc_master_pass,
        "enc_master_rec": enc_master_rec,
        "keys": {}
    }

    with open(VAULT_PATH, 'w') as v:
        json.dump(vault_data, v, indent=2)

    print("\n🔐 SECAPI VAULT INITIALIZED")
    print("------------------------------------------------------------")
    print("Your vault has been initialized with AES-256 encryption.")
    print("Write down your emergency recovery key and store it safely:")
    print(f"\n👉  {recovery_key}  👈\n")
    print("If you forget your password, run: secapi recover")
    print("------------------------------------------------------------\n")

    return Fernet(master_key)

def _migrate_vault_if_needed(vault_data, password):
    """Migrates a legacy flat JSON vault to the new structured PBKDF2 Master Key schema."""
    if not vault_data:
        return vault_data, None
    if "enc_master_pass" in vault_data:
        return vault_data, None
    
    print("⚠️ Legacy vault format detected. Migrating to secure PBKDF2 schema...")
    legacy_key = legacy_derive_key(password)
    legacy_fernet = Fernet(legacy_key)
    
    decrypted_keys = {}
    for k, v in vault_data.items():
        if k in {"salt", "keys"}:
            continue
        try:
            decrypted_keys[k] = legacy_fernet.decrypt(v.encode()).decode()
        except Exception:
            raise ValueError("Invalid password or corrupted legacy vault.")
            
    # Initialize master key system for migrated vault
    master_key = Fernet.generate_key()
    recovery_key = generate_recovery_key()
    
    salt = os.urandom(16)
    recovery_salt = os.urandom(16)
    
    pass_derived_key = derive_key(password, salt)
    rec_derived_key = derive_key(recovery_key, recovery_salt)
    
    f_pass = Fernet(pass_derived_key)
    f_rec = Fernet(rec_derived_key)
    
    enc_master_pass = f_pass.encrypt(master_key).decode()
    enc_master_rec = f_rec.encrypt(master_key).decode()
    
    f_master = Fernet(master_key)
    new_keys = {}
    for k, v in decrypted_keys.items():
        new_keys[k] = f_master.encrypt(v.encode()).decode()
        
    migrated_vault = {
        "salt": base64.b64encode(salt).decode(),
        "recovery_salt": base64.b64encode(recovery_salt).decode(),
        "enc_master_pass": enc_master_pass,
        "enc_master_rec": enc_master_rec,
        "keys": new_keys
    }
    
    print("\n🔐 SECAPI VAULT MIGRATED")
    print("------------------------------------------------------------")
    print("Your vault has been upgraded. Write down your recovery key:")
    print(f"\n👉  {recovery_key}  👈\n")
    print("If you forget your password, run: secapi recover")
    print("------------------------------------------------------------\n")
    
    return migrated_vault, f_master

def get_fernet():
    global _fernet_instance
    if _fernet_instance is not None:
        return _fernet_instance

    password = safe_input("🔐 Enter your master vault password")
    
    vault_data = {}
    if os.path.exists(VAULT_PATH):
        try:
            with open(VAULT_PATH, 'r') as v:
                vault_data = json.load(v)
        except Exception:
            print("❌ Failed to parse vault JSON file.")
            exit(1)

    # Initialize a new vault if empty
    if not vault_data:
        _fernet_instance = _initialize_new_vault(password)
        return _fernet_instance

    # Handle migration if the legacy format is found
    if "enc_master_pass" not in vault_data:
        try:
            vault_data, f = _migrate_vault_if_needed(vault_data, password)
            with open(VAULT_PATH, 'w') as v:
                json.dump(vault_data, v, indent=2)
            _fernet_instance = f
            return f
        except ValueError as e:
            print(f"❌ {e}")
            exit(1)
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            exit(1)

    # Load standard secure format
    salt_b64 = vault_data.get("salt")
    enc_master_pass = vault_data.get("enc_master_pass")
    try:
        salt = base64.b64decode(salt_b64.encode())
        key = derive_key(password, salt)
        f_pass = Fernet(key)
        master_key = f_pass.decrypt(enc_master_pass.encode())
        _fernet_instance = Fernet(master_key)
    except Exception:
        print("❌ Invalid password for the current vault.")
        exit(1)

    return _fernet_instance

def recover_vault():
    """Recover the vault using the recovery key and set a new password."""
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    try:
        with open(VAULT_PATH, 'r') as f:
            vault_data = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read vault: {e}")
        return

    if "enc_master_rec" not in vault_data or "recovery_salt" not in vault_data:
        print("❌ This vault does not support recovery keys. Please start fresh by deleting the vault file.")
        return

    recovery_key = input("🔑 Enter your 24-character recovery key (e.g. XXXX-XXXX-XXXX-XXXX-XXXX-XXXX): ").strip()
    recovery_salt_b64 = vault_data["recovery_salt"]
    enc_master_rec = vault_data["enc_master_rec"]

    try:
        recovery_salt = base64.b64decode(recovery_salt_b64.encode())
        rec_derived_key = derive_key(recovery_key, recovery_salt)
        f_rec = Fernet(rec_derived_key)
        master_key = f_rec.decrypt(enc_master_rec.encode())
    except Exception:
        print("❌ Invalid recovery key. Recovery failed.")
        return

    print("🔓 Recovery key verified! Please set a new master password.")
    new_pass = getpass("🔐 Enter new master password: ")
    confirm = getpass("🔁 Confirm new password: ")
    if new_pass != confirm:
        print("❌ Passwords do not match. Recovery aborted.")
        return

    # Re-encrypt master key under new password
    new_salt = os.urandom(16)
    new_pass_key = derive_key(new_pass, new_salt)
    f_pass = Fernet(new_pass_key)
    new_enc_master_pass = f_pass.encrypt(master_key).decode()

    vault_data["salt"] = base64.b64encode(new_salt).decode()
    vault_data["enc_master_pass"] = new_enc_master_pass

    with open(VAULT_PATH, 'w') as f:
        json.dump(vault_data, f, indent=2)

    print("✅ Vault recovered successfully. You can now access it with your new password!")

def change_vault_password():
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    try:
        # Decrypt master key under old password
        old_fernet = get_fernet() 
        with open(VAULT_PATH, 'r') as f:
            vault_data = json.load(f)

        # Retrieve the master key
        salt_b64 = vault_data.get("salt")
        enc_master_pass = vault_data.get("enc_master_pass")
        salt = base64.b64decode(salt_b64.encode())
        
        # Request new password
        new_pass = getpass("🔐 Enter your new master password: ")
        confirm = getpass("🔁 Confirm new password: ")
        if new_pass != confirm:
            print("❌ Passwords do not match.")
            return

        # Fetch decrypted master key
        # We need the bytes value of the master key itself
        # Currently _fernet_instance contains Fernet(master_key)
        # We can extract it by decrypting the enc_master_pass with old_fernet
        # Wait, get_fernet already populated _fernet_instance, which is the master key Fernet.
        # But we can also get master_key by calling old_fernet decrypt
        # Actually, get_fernet returns the master key Fernet, but we need the raw master_key bytes to re-encrypt it.
        # Let's read it directly using old password key:
        # The password key derived from old password is what decrypted enc_master_pass.
        # Wait, get_fernet returns the master key Fernet. But wait! Can we decrypt an empty string to get master key? No.
        # But since we have get_fernet, we can just decrypt any value in vault using _fernet_instance,
        # but that is the master key.
        # Wait, let's look at get_fernet implementation:
        # password -> pass_derived_key -> decrypts enc_master_pass -> master_key.
        # So we can decrypt enc_master_pass with the key derived from old password.
        # Wait, in change_vault_password, we run get_fernet(), which asks for old password and sets _fernet_instance.
        # Wait, since get_fernet asks for old password and derives the master key, we can store the raw master key
        # globally as _master_key_bytes or get it from _fernet_instance!
        # Wait! Can we extract the key from a Fernet instance?
        # Yes! Fernet class stores the key in `_signing_key` and `_encryption_key`, or we can just access `f._key`!
        # Yes! `f._key` is a public property in cryptography's Fernet!
        # Let's verify: `f._key` returns the original 32-byte key!
        # That is extremely simple: `master_key = old_fernet._key`!
        # Let's use that!
        master_key = old_fernet._key

        new_salt = os.urandom(16)
        new_key = derive_key(new_pass, new_salt)
        new_fernet = Fernet(new_key)
        new_enc_master_pass = new_fernet.encrypt(master_key).decode()

        vault_data["salt"] = base64.b64encode(new_salt).decode()
        vault_data["enc_master_pass"] = new_enc_master_pass

        with open(VAULT_PATH, 'w') as f:
            json.dump(vault_data, f, indent=2)

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

    with open(VAULT_PATH, 'r') as v:
        vault = json.load(v)

    keys_dict = vault.setdefault("keys", {})
    if key_name in keys_dict:
        print(f"⚠️ Key '{key_name}' already exists. Overwriting...")

    keys_dict[key_name] = {
        "value": encrypted,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    with open(VAULT_PATH, 'w') as v:
        json.dump(vault, v, indent=2)

    print(f"✅ Key '{key_name}' securely stored in your vault.")
    print("\n🔁 Use it in your code like this:")
    print(f"    {key_name} = load_key(\"{key_name}\")\n")

def load_key(key_name):
    if not os.path.exists(VAULT_PATH):
        raise FileNotFoundError("Vault not found. Please run the CLI first.")

    with open(VAULT_PATH, 'r') as v:
        vault = json.load(v)

    keys_dict = vault.get("keys", {})
    if key_name not in keys_dict:
        raise KeyError(f"Key '{key_name}' not found in the vault.")

    fernet = get_fernet()
    encrypted_data = keys_dict[key_name]
    
    if isinstance(encrypted_data, dict):
        encrypted = encrypted_data["value"]
        created_at_str = encrypted_data.get("created_at")
    else:
        encrypted = encrypted_data
        created_at_str = None

    decrypted = fernet.decrypt(encrypted.encode()).decode()

    # Warn if key is expired/nearing expiration
    if created_at_str:
        try:
            from secapi.config import get_rotation_interval_days
            interval = get_rotation_interval_days()
            created_at = datetime.datetime.fromisoformat(created_at_str)
            age_days = (datetime.datetime.utcnow() - created_at).days
            if age_days >= interval:
                print(f"\033[1;31m⚠️ Warning: Vault key '{key_name}' has EXPIRED ({age_days} days old). Please rotate it! \033[0m")
            elif age_days >= (interval - 5):
                print(f"\033[1;33m⚠️ Warning: Vault key '{key_name}' is nearing expiration ({age_days} days old). \033[0m")
        except Exception:
            pass

    return decrypted

def list_keys():
    if not os.path.exists(VAULT_PATH):
        print("🔒 No keys stored yet.")
        return

    with open(VAULT_PATH, 'r') as f:
        vault = json.load(f)

    keys_dict = vault.get("keys", {})
    if not keys_dict:
        print("🔒 No keys stored yet.")
        return

    from secapi.config import get_rotation_interval_days
    interval = get_rotation_interval_days()

    # Terminal Dashboard Layout
    env_str = f" [Profile: {CURRENT_ENV.upper()}]" if CURRENT_ENV else ""
    print(f"\n🔑 \033[1;36mSECAPI SECURE VAULT DASHBOARD{env_str}\033[0m")
    print("=" * 72)
    print(f"\033[1m{'Key Name':<28} | {'Status':<15} | {'Age (Days)':<10} | {'Created At':<10}\033[0m")
    print("-" * 72)

    for key, val in keys_dict.items():
        created_at_str = None
        if isinstance(val, dict):
            created_at_str = val.get("created_at")

        if created_at_str:
            try:
                created_at = datetime.datetime.fromisoformat(created_at_str)
                age_days = (datetime.datetime.utcnow() - created_at).days
                date_str = created_at.strftime("%Y-%m-%d")
                age_str = str(age_days)
            except Exception:
                age_days = 0
                age_str = "0"
                date_str = "Error"
        else:
            age_days = None
            age_str = "N/A"
            date_str = "Legacy"

        # Determine status color
        if age_days is None:
            status = "\033[1;33m⚠️ Unknown\033[0m"
        else:
            if age_days >= interval:
                status = "\033[1;31m🔴 Expired\033[0m"
            elif age_days >= (interval - 5):
                status = "\033[1;33m🟡 Rotate Soon\033[0m"
            else:
                status = "\033[1;32m🟢 Active\033[0m"

        print(f"{key:<28} | {status:<24} | {age_str:<10} | {date_str:<10}")
    print("=" * 72 + "\n")

def delete_key(key_name):
    if not os.path.exists(VAULT_PATH):
        print("❌ Vault not found.")
        return

    fernet = get_fernet()

    with open(VAULT_PATH, 'r') as f:
        vault = json.load(f)

    keys_dict = vault.get("keys", {})
    if key_name in keys_dict:
        del keys_dict[key_name]
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

    keys_dict = vault.get("keys", {})
    if key_name not in keys_dict:
        print(f"❌ Key '{key_name}' not found in the vault.")
        return

    new_value = safe_input(f"🔁 Enter new value for key '{key_name}'").strip()
    fernet = get_fernet()
    encrypted = fernet.encrypt(new_value.encode()).decode()
    
    keys_dict[key_name] = {
        "value": encrypted,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    with open(VAULT_PATH, 'w') as f:
        json.dump(vault, f, indent=2)
    print(f"🔁 Key '{key_name}' rotated successfully.")

def update_vault(key_name, encrypted):
    """Update the vault with the new encrypted secret."""
    try:
        vault = {}
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, 'r') as v:
                vault = json.load(v)

        keys_dict = vault.setdefault("keys", {})
        keys_dict[key_name] = {
            "value": encrypted,
            "created_at": datetime.datetime.utcnow().isoformat()
        }
        with open(VAULT_PATH, 'w') as v:
            json.dump(vault, v, indent=2)
    except Exception as e:
        print(f"❌ Failed to update vault: {e}")
        raise


