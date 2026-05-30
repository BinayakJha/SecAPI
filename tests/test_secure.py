import os
import json
import base64
import pytest
from unittest.mock import patch
from cryptography.fernet import Fernet

from secapi import secure

@pytest.fixture(autouse=True)
def clear_fernet_cache():
    """Clear cached global Fernet instance before and after each test."""
    secure._fernet_instance = None
    yield
    secure._fernet_instance = None

def test_legacy_derive_key():
    key = secure.legacy_derive_key("password")
    assert len(key) == 44  # Base64 Fernet key length

def test_derive_key():
    salt = os.urandom(16)
    key1 = secure.derive_key("password", salt)
    key2 = secure.derive_key("password", salt)
    assert key1 == key2

    key3 = secure.derive_key("different_password", salt)
    assert key1 != key3

def test_vault_flow(tmp_path, monkeypatch):
    vault_file = tmp_path / "vault.json"
    monkeypatch.setattr(secure, "VAULT_PATH", str(vault_file))

    # Mock safe_input to return values dynamically
    def mock_safe_input(prompt):
        if "master" in prompt or "password" in prompt:
            return "test_password"
        if "API key" in prompt:
            return "sk_test_12345"
        return "test_password"

    monkeypatch.setattr(secure, "safe_input", mock_safe_input)

    # 1. Verify vault is initialized on first get_fernet call
    assert not vault_file.exists()
    f = secure.get_fernet()
    assert vault_file.exists()

    with open(vault_file, 'r') as v:
        vault_data = json.load(v)
    assert "salt" in vault_data
    assert "keys" in vault_data
    assert vault_data["keys"] == {}

    # 2. Mock input for adding a key
    inputs = ["my_stripe_key"]
    monkeypatch.setattr("builtins.input", lambda prompt="": inputs.pop(0))

    secure.add_key_interactively()

    # 3. Verify file content and loading the key
    with open(vault_file, 'r') as v:
        vault_data = json.load(v)
    assert "my_stripe_key" in vault_data["keys"]

    val = secure.load_key("my_stripe_key")
    assert val == "sk_test_12345"

    # 4. List keys
    with patch('builtins.print') as mock_print:
        secure.list_keys()
        printed_msgs = [call[0][0] for call in mock_print.call_args_list if call[0]]
        assert any("my_stripe_key" in str(msg) for msg in printed_msgs)

    # 5. Delete key
    secure.delete_key("my_stripe_key")
    with open(vault_file, 'r') as v:
        vault_data = json.load(v)
    assert "my_stripe_key" not in vault_data["keys"]

def test_migration(tmp_path, monkeypatch):
    vault_file = tmp_path / "vault.json"
    monkeypatch.setattr(secure, "VAULT_PATH", str(vault_file))

    # Create a legacy format vault
    password = "migrate_password"
    legacy_key = secure.legacy_derive_key(password)
    legacy_fernet = Fernet(legacy_key)

    legacy_data = {
        "stripe": legacy_fernet.encrypt(b"sk_test_legacy").decode(),
        "openai": legacy_fernet.encrypt(b"sk-legacy-openai").decode()
    }
    with open(vault_file, 'w') as f:
        json.dump(legacy_data, f)

    # Mock password entry
    monkeypatch.setattr(secure, "safe_input", lambda prompt: password)

    # get_fernet triggers migration
    f = secure.get_fernet()

    # Check migrated structure
    with open(vault_file, 'r') as v:
        migrated_data = json.load(v)

    assert "salt" in migrated_data
    assert "keys" in migrated_data
    assert "stripe" in migrated_data["keys"]
    assert "openai" in migrated_data["keys"]

    # Verify keys decrypt properly under the new scheme
    assert secure.load_key("stripe") == "sk_test_legacy"
    assert secure.load_key("openai") == "sk-legacy-openai"

def test_recovery(tmp_path, monkeypatch):
    vault_file = tmp_path / "vault.json"
    monkeypatch.setattr(secure, "VAULT_PATH", str(vault_file))

    # Mock safe_input to return values dynamically
    recovery_key = []
    original_print = print

    def mock_print(*args, **kwargs):
        msg = " ".join(map(str, args))
        if "👉" in msg:
            # Extract key: e.g. "👉  A1B2-C3D4-...  👈"
            key = msg.split("👉")[1].split("👈")[0].strip()
            recovery_key.append(key)
        original_print(*args, **kwargs)

    monkeypatch.setattr("builtins.print", mock_print)
    monkeypatch.setattr(secure, "safe_input", lambda prompt: "old_password")

    # 1. Initialize vault
    secure.get_fernet()
    assert len(recovery_key) == 1
    rec_key = recovery_key[0]

    # Add a mock key
    inputs = ["my_secret"]
    monkeypatch.setattr("builtins.input", lambda prompt="": inputs.pop(0))
    monkeypatch.setattr(secure, "safe_input", lambda prompt: "my_secret_val" if "API key" in prompt else "old_password")
    secure.add_key_interactively()

    # Clear cached global Fernet
    secure._fernet_instance = None

    # 2. Run recovery using the recovery key and setting new password "new_password"
    recovery_inputs = [rec_key]
    monkeypatch.setattr("builtins.input", lambda prompt="": recovery_inputs.pop(0))
    
    getpass_inputs = ["new_password", "new_password"]
    monkeypatch.setattr(secure, "getpass", lambda prompt: getpass_inputs.pop(0))

    secure.recover_vault()

    # Clear cached global Fernet again
    secure._fernet_instance = None

    # 3. Access key using the new password
    monkeypatch.setattr(secure, "safe_input", lambda prompt: "new_password")
    val = secure.load_key("my_secret")
    assert val == "my_secret_val"

def test_env_profiles():
    import os
    secure.set_current_env(None)
    assert secure.VAULT_PATH == os.path.expanduser("~/.secapi_vault.json")

    secure.set_current_env("staging")
    assert secure.VAULT_PATH == os.path.expanduser("~/.secapi_vault_staging.json")

    secure.set_current_env(None)

def test_ttl_warning(tmp_path, monkeypatch):
    import datetime
    from unittest.mock import patch

    vault_file = tmp_path / "vault.json"
    monkeypatch.setattr(secure, "VAULT_PATH", str(vault_file))
    monkeypatch.setattr(secure, "safe_input", lambda prompt: "pwd")

    # Initialize vault
    secure.get_fernet()

    # Encrypt a secret
    encrypted = secure._fernet_instance.encrypt(b"secret_value").decode()
    expired_date = (datetime.datetime.utcnow() - datetime.timedelta(days=40)).isoformat()

    with open(vault_file, 'r') as v:
        vault_data = json.load(v)

    vault_data["keys"]["expired_key"] = {
        "value": encrypted,
        "created_at": expired_date
    }
    with open(vault_file, 'w') as v:
        json.dump(vault_data, v)

    # Verify expiration warning is printed on load
    with patch('builtins.print') as mock_print:
        val = secure.load_key("expired_key")
        assert val == "secret_value"
        printed_msgs = [call[0][0] for call in mock_print.call_args_list if call[0]]
        assert any("EXPIRED" in msg for msg in printed_msgs)


