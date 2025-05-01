import argparse
from secapi.scanner import scan_directory
from secapi.fixer import suggest_and_fix
from secapi.secure import load_key, list_keys, delete_key, rotate_key, change_vault_password  # assuming you also move these here
from secapi.scanner_ai import ai_scan_path
from secapi.secure import add_key_interactively
from secapi.agent import run_agent

def main():
    parser = argparse.ArgumentParser(
        description="SecAPI - Secure your API keys before they leak."
    )
    parser.add_argument(
        "command", metavar="command", type=str,
        choices=[
            "check", "list", "delete", "rotate", "load", "ai", "add", "agent", "change-password"
        ],
        help="Command to run: check <dir> | list | delete <key_name> | rotate <key_name> | load <key_name> | agent | change-password"
    )
    parser.add_argument("value", nargs="?", help="Path, key name, or file depending on the command.")

    args = parser.parse_args()

    if args.command == "agent":
        run_agent()

    elif args.command == "list":
        list_keys()
    elif args.command == "delete":
        if not args.value:
            print("❌ Please provide a key name to delete.")
            return
        delete_key(args.value)
    elif args.command == "rotate":
        if not args.value:
            print("❌ Please provide a key name to rotate.")
            return
        rotate_key(args.value)
    elif args.command == "load":
        if not args.value:
            print("❌ Please provide a key name to load.")
            return
        value = load_key(args.value)
        print(f"🔓 Value for '{args.value}': {value}")
    
    elif args.command == "ai":
        if not args.value:
            print("❌ Please provide a file path to scan with AI.")
            return
        ai_scan_path(args.value)

    elif args.command == "add":
        add_key_interactively()
        return
    elif args.command == "change-password":
        change_vault_password()
        return
    elif args.command == "check":
        if not args.value:
            print("❌ Please provide a directory path to scan.")
            return
        print(f"\n🔍 Scanning directory: {args.value}\n")
        findings = scan_directory(args.value)
        if not findings:
            print("✅ No secrets found. You're all clean!")
            return
        for idx, (file, line_num, line_content, match) in enumerate(findings):
            print(f"[{idx + 1}] 🔑 Potential secret in {file} at line {line_num}:")
            print(f"    {line_content.strip()}")
            print(f"    ➤ Matched pattern: {match}\n")
        for finding in findings:
            suggest_and_fix(*finding)

if __name__ == "__main__":
    main()
