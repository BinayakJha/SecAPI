# Regex-based scanner

import os
import re
import fnmatch

# Common API key patterns
PATTERNS = {
    "Stripe": r"sk_(live|test)_[0-9a-zA-Z]{24,}",
    "Google": r"AIza[0-9A-Za-z\-_]{35}",
    "GitHub": r"ghp_[A-Za-z0-9]{36}",
    "Slack": r"xox[baprs]-[A-Za-z0-9-]+",
    "OpenAI": r"sk-[A-Za-z0-9]{32,}",  # OpenAI API keys
    "Microsoft Graph": r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",  # GUIDs for client IDs/tenant IDs
    "AWS Access Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Key": r"(?i)aws_secret_access_key[\s\"']*[:=][\s\"']*[0-9a-zA-Z/+]{40}",
    "Twilio": r"SK[0-9a-f]{32}",
    "Heroku": r"heroku_[0-9a-f]{32}",
    "SendGrid": r"SG\.[A-Za-z0-9\-_]{22}\.[A-Za-z0-9\-_]{43}",
    "Dropbox": r"sl\.[A-Za-z0-9\-_]{15,}",
    "Generic": r"(?i)(api|secret|token|key)[\s\"']*[:=][\s\"']*[0-9a-zA-Z\-\._]{16,}"
}

def load_ignore_patterns(directory):
    """Load ignore patterns from a .secapiignore file if it exists."""
    patterns = []
    ignore_file = os.path.join(directory, '.secapiignore')
    if os.path.exists(ignore_file):
        try:
            with open(ignore_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"⚠️ Failed to read .secapiignore: {e}")
    return patterns

def should_ignore(path, root_dir, patterns):
    """Check if the given path should be ignored based on default patterns or .secapiignore."""
    rel_path = os.path.relpath(path, root_dir)
    parts = rel_path.split(os.sep)

    # 1. Default directory exclusions
    default_excludes = {
        '.git', 'node_modules', '.venv', 'venv', 'env', '__pycache__',
        'build', 'dist', '.eggs', '.idea', '.vscode', '.mypy_cache', '.pytest_cache'
    }
    for part in parts:
        if part in default_excludes:
            return True

    # 2. Custom patterns from .secapiignore
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
        if fnmatch.fnmatch(rel_path + '/', pattern) or any(fnmatch.fnmatch(p, pattern) for p in parts):
            return True

    return False

def scan_directory(directory):
    findings = []
    patterns = load_ignore_patterns(directory)

    for root, dirs, files in os.walk(directory, topdown=True):
        # Filter directory traversal to avoid ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), directory, patterns)]

        for file in files:
            path = os.path.join(root, file)
            if should_ignore(path, directory, patterns):
                continue

            if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml', '.yaml', '.txt')):
                try:
                    with open(path, 'r', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            # Skip lines that are importing or using secure retrieval methods
                            if "load_key" in line or "os.environ" in line or "os.getenv" in line:
                                continue
                            for label, pattern in PATTERNS.items():
                                match = re.search(pattern, line)
                                if match:
                                    findings.append((path, i, line.strip(), label))
                                    break
                except (PermissionError, IsADirectoryError, UnicodeDecodeError):
                    pass  # Silently skip unreadable or invalid files
    return findings