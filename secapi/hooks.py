# secapi/hooks.py (Git Hooks Integration)

import os
import stat

def install_pre_commit_hook():
    """Installs a git pre-commit hook in the current working directory."""
    git_dir = ".git"
    if not os.path.exists(git_dir) or not os.path.isdir(git_dir):
        print("❌ Error: Not in a git repository (could not find '.git' directory).")
        return False

    hooks_dir = os.path.join(git_dir, "hooks")
    os.makedirs(hooks_dir, exist_ok=True)

    hook_file = os.path.join(hooks_dir, "pre-commit")

    hook_script = """#!/bin/sh
# SecAPI Pre-commit Hook
echo "🔍 SecAPI: Scanning codebase for hardcoded secrets before commit..."

# Run secapi check in the repository root in report-only mode
secapi check . --no-fix

status=$?
if [ $status -ne 0 ]; then
    echo "❌ SecAPI: Commit blocked. Please secure your API keys before committing!"
    exit 1
fi
echo "✅ SecAPI: Scan completed. Code is clean!"
"""

    if os.path.exists(hook_file):
        with open(hook_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if "SecAPI Pre-commit Hook" in content:
            print("ℹ️ SecAPI pre-commit hook is already installed.")
            return True

        print("⚠️ An existing pre-commit hook was found. Appending SecAPI scanner...")
        hook_script_append = "\n" + "\n".join(hook_script.splitlines()[1:])
        with open(hook_file, 'a', encoding='utf-8') as f:
            f.write(hook_script_append)
    else:
        with open(hook_file, 'w', encoding='utf-8') as f:
            f.write(hook_script)

    # Set executable permissions: chmod +x
    try:
        st = os.stat(hook_file)
        os.chmod(hook_file, st.st_mode | stat.S_IEXEC)
        print("✅ Git pre-commit hook installed successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to set executable permissions on hook: {e}")
        return False
