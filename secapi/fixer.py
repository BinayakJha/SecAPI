# Handles encryption and replacement
import os
import re
from secapi.secure import load_key, get_fernet, update_vault

def update_file(file, line_num, key_name):
    """
    Updates the specified line in the file to replace the hardcoded secret
    with a secure reference using `load_key()`.
    Preserves the original variable name (LHS).
    """
    try:
        with open(file, 'r') as f_in:
            lines = f_in.readlines()

        # Check if load_key is already imported in the file
        has_import = any("load_key" in line for line in lines)
        target_idx = line_num - 1

        if not has_import:
            insert_idx = 0
            if lines and (lines[0].startswith('#!') or lines[0].startswith('# -*-')):
                insert_idx = 1
            lines.insert(insert_idx, "from secapi.secure import load_key\n")
            target_idx += 1  # Shifted due to insertion

        target_line = lines[target_idx]
        
        # Match pattern: indentation, variable/LHS, '=', quotes, secret, quotes, trailing
        # Regex explanation:
        # ^(\s*)       -> Group 1: Leading indentation
        # ([A-Za-z0-9_\-\[\]\'"\.]+) -> Group 2: LHS (variable name, config key, etc.)
        # \s*=\s*      -> assignment operator with optional spaces
        # (["\'])      -> Group 3: Opening quote
        # (.*?)        -> Group 4: The secret string
        # \3           -> Match corresponding closing quote
        # (.*)$        -> Group 5: Trailing comments/whitespace
        pattern = r'^(\s*)([A-Za-z0-9_\-\[\]\'"\.]+)\s*=\s*(["\'])(.*?)\3(.*)$'
        match = re.match(pattern, target_line)
        
        if match:
            indent = match.group(1)
            lhs = match.group(2)
            trailing = match.group(5)
            new_line = f'{indent}{lhs} = load_key("{key_name}"){trailing}\n'
            lines[target_idx] = new_line
        else:
            # Fallback if the match is not a standard assignment
            new_line = f'{key_name} = load_key("{key_name}")\n'
            lines[target_idx] = new_line

        with open(file, 'w') as f_out:
            f_out.writelines(lines)

        print(f"✅ Updated file '{file}' to use secure reference for '{key_name}'.")
    except Exception as e:
        print(f"❌ Failed to update file '{file}': {e}")
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
            
            # Find the secret string enclosed in quotes
            key_match = re.search(r'["\'](.*?)["\']', line_content)
            if key_match:
                secret = key_match.group(1)
                encrypted = fernet.encrypt(secret.encode()).decode()
                key_name = input("Give this key a name (e.g., 'openai_key'): ").strip()

                if not key_name:
                    print("❌ Key name cannot be empty. Skipping.")
                    return

                # Update the file and vault
                update_file(file, line_num, key_name)
                update_vault(key_name, encrypted)
            else:
                print("❌ No valid secret string literal found in quotes.")
        except Exception as e:
            print(f"❌ Failed to process the secret: {e}")
    elif choice == "3":
        print("⚠️  Skipped.")
    else:
        print("❌ Invalid choice. Skipping.")