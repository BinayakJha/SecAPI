from sentinel.secure import load_key
import os
import re
import json
from getpass import getpass
from openai import OpenAI
from cryptography.fernet import Fernet
from sentinel.secure import get_fernet, VAULT_PATH


def ai_scan_file(file_path):
    token = load_key("gt_token")
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"

    client = OpenAI(
        base_url=endpoint,
        api_key=token,
    )

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()[:4000]  # trim to fit token limit

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
        lines = output.split("\n")

        line_num = None
        code_line = None

        for idx, line in enumerate(lines):
            if "🧪" in line and re.match(r"\s*🧪\s*\d+:", line):
                try:
                    match = re.match(r"\s*🧪\s*(\d+):\s*(.+)", line.strip())
                    line_num = int(match.group(1))
                    code_line = match.group(2)
                    print(f"    🧪 {line_num}: {code_line}")
                except:
                    print(f"hahaahaha")
                    continue
            # If we captured line number and code_line
            if line_num and code_line:
                print("\n🔧 Do you want to fix this?")
                print("  [1] Replace with load_key()")
                print("  [2] Move to .env (manual)")
                print("  [3] Ignore")
                choice = input("Select an option: ").strip()

                if choice == "1":
                    key_name = input(
                        "Give this key a name (e.g., 'openai_key'): ").strip()
                    secret = code_line.split("=")[1].strip().strip('"')
                    print(secret)

                    fernet = get_fernet()
                    encrypted = fernet.encrypt(secret.encode()).decode()

                    with open(file_path, 'r') as f:
                        all_lines = f.readlines()

                    # Check if load_key is already imported
                    if not any("load_key" in line for line in all_lines[:line_num]):
                        all_lines.insert(
                            1, "from sentinel.secure import load_key\n")
                    # Replace the line with load_key
                    # if there is indent in the line_num then add indent or not also dont replace the variable name
                    variable_name = code_line.split("=")[0].strip()
                    target_line = all_lines[line_num + 1]
                    indent_match = re.match(r"^\\s*", target_line)
                    indent = indent_match.group(0) if indent_match else ""

                    # Replace the line with correctly indented load_key()
                    all_lines[line_num +
                              1] = f"{indent}{variable_name} = load_key(\"{key_name}\")\n"

                    with open(file_path, 'w') as f:
                        f.writelines(all_lines)

                    if os.path.exists(VAULT_PATH):
                        with open(VAULT_PATH, 'r') as v:
                            vault = json.load(v)
                    else:
                        vault = {}

                    vault[key_name] = encrypted
                    with open(VAULT_PATH, 'w') as v:
                        json.dump(vault, v, indent=2)

                    print(
                        f"✅ Replaced and stored key '{key_name}' securely.\n")
                    # Reset
                    line_num = None
                    code_line = None
                elif choice == "3":
                    line_num = None
                    code_line = None

    except Exception as e:
        print(f"❌ AI scan failed: {e}")

def ai_scan_path(path):
    if os.path.isfile(path):
        ai_scan_file(path)
    elif os.path.isdir(path):
        print(f"\n📁 Scanning folder: {path}\n")
        for root, _, files in os.walk(path):
            for file in files:
                print(f"🔍 Scanning file: {file}")
                if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml')):
                    full_path = os.path.join(root, file)
                    ai_scan_file(full_path)
    else:
        print(f"❌ Invalid path: {path}")
