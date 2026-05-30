import os
import re
import json
from secapi.secure import load_key, get_fernet, update_vault
from secapi.config import get_ai_config
from secapi.gemini import call_gemini

def ai_scan_file(file_path):
    """Scan a single file for hardcoded secrets using AI, with line-aware chunking."""
    ai_config = get_ai_config()
    provider = ai_config["provider"]
    model = ai_config["model"]
    api_key = ai_config["api_key"]
    endpoint = ai_config["endpoint"]

    if not api_key:
        print("❌ Warning: AI API key not found in config, env, or vault. Skipping AI scan.")
        return

    client = None
    if provider == "azure":
        try:
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_key=api_key,
                api_version="2023-07-01-preview",
                azure_endpoint=endpoint
            )
        except ImportError:
            print("❌ Error: The 'openai' library is missing or outdated.")
            print("Please upgrade it using: pip install --upgrade openai")
            return
    elif provider == "openai":
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url=endpoint
            )
        except ImportError:
            print("❌ Error: The 'openai' library is missing or outdated.")
            print("Please upgrade it using: pip install --upgrade openai")
            return

    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read()

        lines = content.splitlines()
        chunks = []
        current_chunk = []
        current_length = 0

        # Chunk the file while prefixing each line with its 1-based index
        for i, line in enumerate(lines, 1):
            formatted_line = f"{i}: {line}"
            if current_length + len(formatted_line) + 1 > 3500:
                chunks.append("\n".join(current_chunk))
                current_chunk = [formatted_line]
                current_length = len(formatted_line)
            else:
                current_chunk.append(formatted_line)
                current_length += len(formatted_line) + 1
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        print(f"\n🔍 AI Security Audit (using {provider}/{model}):")
        print(f"📄 File: {file_path} ({len(chunks)} chunks)")

        for chunk_idx, chunk_content in enumerate(chunks, 1):
            if len(chunks) > 1:
                print(f"  ⚡ Scanning chunk {chunk_idx}/{len(chunks)}...")

            system_content = """
            You are a source code security auditor. 

            Your job is to scan the code for hardcoded secrets or insecure API key usage. 
            Each line in the input is prefixed with its 1-based line number (e.g. "12: api_key = 'sk_...'").
            
            ❌ Do NOT return lines that already use secure retrieval methods like `load_key(...)` or environment variables like `os.environ[...]`. 

            ✅ Only return lines that directly assign hardcoded secrets.

            Output format (strict):
            🧪 <line_number>: <variable_name> = <secret_string>

            Only return one line per issue. No explanations.
            """

            if provider == "gemini":
                output = call_gemini(
                    system_instruction=system_content,
                    messages=[{"role": "user", "content": f"Filename: {file_path}\n\n{chunk_content}"}],
                    model=model,
                    api_key=api_key
                )
            else:
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": system_content
                        },
                        {
                            "role": "user",
                            "content": f"Filename: {file_path}\n\n{chunk_content}"
                        }
                    ],
                    model=model,
                    temperature=0.2,
                    top_p=1.0
                )
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
        if not key_name:
            print("❌ Key name cannot be empty. Skipping.")
            return

        parts = code_line.split("=", 1)
        if len(parts) < 2:
            print("❌ Could not parse secret from AI output. Skipping.")
            return

        secret = parts[1].strip().strip('"').strip("'")
        fernet = get_fernet()
        encrypted = fernet.encrypt(secret.encode()).decode()

        from secapi.fixer import update_file
        update_file(file_path, line_num, key_name)
        update_vault(key_name, encrypted)
        print(f"✅ Replaced and stored key '{key_name}' securely.\n")

    except Exception as e:
        print(f"❌ Failed to replace secret: {e}")



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
