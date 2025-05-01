import os
import re
import json
from getpass import getpass
from openai import OpenAI
from cryptography.fernet import Fernet
from secapi.secure import load_key, get_fernet, VAULT_PATH


def ai_scan_file(file_path):
    """Scan a single file for hardcoded secrets using AI."""
    token = load_key("gt_token")
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()[:4000]  # Trim to fit token limit

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a source code security auditor. 

                    Your job is to scan the code for hardcoded secrets or insecure API key usage. 
                    ❌ Do NOT return lines that already use secure retrieval methods like `load_key(...)` or environment variables like `os.environ[...]`. 

                    ✅ Only return lines that directly assign hardcoded secrets.

                    Output format (strict):
                    🧪 <line_number>: <variable_name> = <secret_string>

                    Only return one line per issue. No explanations.
                    """
                },
                {
                    "role": "user",
                    "content": f"Filename: {file_path}\n\n{content}"
                }
            ],
            model=model,
            temperature=0.2,
            top_p=1.0
        )

        print("\n🔍 AI Security Audit:")
        print(f"📄 File: {file_path}\n")

        output = response.choices[0].message.content
        process_ai_output(output, file_path)

    except Exception as e:
        print(f"❌ AI scan failed: {e}")


def process_ai_output(output, file_path):
    """Process the AI output and handle user choices."""
    lines = output.split("\n")
    for line in lines:
        if "🧪" in line and re.match(r"\s*🧪\s*\d+:", line):
            try:
                match = re.match(r"\s*🧪\s*(\d+):\s*(.+)", line.strip())
                line_num = int(match.group(1))
                code_line = match.group(2)
                print(f"    🧪 {line_num}: {code_line}")
                handle_user_choice(file_path, line_num, code_line)
            except Exception as e:
                print(f"❌ Error processing line: {line}. Error: {e}")


def handle_user_choice(file_path, line_num, code_line):
    """Handle user input for fixing or ignoring detected issues."""
    print("\n🔧 Do you want to fix this?")
    print("  [1] Replace with load_key()")
    print("  [2] Move to .env (manual)")
    print("  [3] Ignore")
    choice = input("Select an option: ").strip()

    if choice == "1":
        replace_with_load_key(file_path, line_num, code_line)
    elif choice == "2":
        print("⚠️ Please move the secret to a .env file manually.")
    elif choice == "3":
        print("✅ Issue ignored.")
    else:
        print("❌ Invalid choice. Skipping.")


def replace_with_load_key(file_path, line_num, code_line):
    """Replace hardcoded secrets with `load_key()` and store them securely."""
    try:
        key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()
        secret = code_line.split("=")[1].strip().strip('"')

        fernet = get_fernet()
        encrypted = fernet.encrypt(secret.encode()).decode()

        with open(file_path, 'r') as f:
            all_lines = f.readlines()

        # Check if load_key is already imported
        if not any("load_key" in line for line in all_lines[:line_num]):
            all_lines.insert(1, "from secapi.secure import load_key\n")

        # Replace the line with load_key
        variable_name = code_line.split("=")[0].strip()
        indent = re.match(r"^\s*", all_lines[line_num - 1]).group(0)
        all_lines[line_num - 1] = f"{indent}{variable_name} = load_key(\"{key_name}\")\n"

        with open(file_path, 'w') as f:
            f.writelines(all_lines)

        # Update the vault
        update_vault(key_name, encrypted)
        print(f"✅ Replaced and stored key '{key_name}' securely.\n")

    except Exception as e:
        print(f"❌ Failed to replace secret: {e}")


def update_vault(key_name, encrypted):
    """Update the vault with the new encrypted secret."""
    try:
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, 'r') as v:
                vault = json.load(v)
        else:
            vault = {}

        vault[key_name] = encrypted
        with open(VAULT_PATH, 'w') as v:
            json.dump(vault, v, indent=2)
    except Exception as e:
        print(f"❌ Failed to update vault: {e}")


def ai_scan_path(path):
    """Scan a file or directory for hardcoded secrets."""
    if os.path.isfile(path):
        ai_scan_file(path)
    elif os.path.isdir(path):
        print(f"\n📁 Scanning folder: {path}\n")
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml')):
                    full_path = os.path.join(root, file)
                    print(f"🔍 Scanning file: {full_path}")
                    ai_scan_file(full_path)
    else:
        print(f"❌ Invalid path: {path}")
