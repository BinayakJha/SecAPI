# Regex-based scanner

import os
import re

# Common API key patterns
PATTERNS = {
    "Stripe": r"sk_live_[0-9a-zA-Z]{24,}",
    "Google": r"AIza[0-9A-Za-z\-_]{35}",
    "GitHub": r"ghp_[A-Za-z0-9]{36}",
    "Slack": r"xox[baprs]-[A-Za-z0-9-]+",
    "Generic": r"(?i)(api|secret|token)[\s\"']*[:=][\s\"']*[0-9a-zA-Z\-\._]{16,}"
}

def scan_directory(directory):
    findings = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            for label, pattern in PATTERNS.items():
                                match = re.search(pattern, line)
                                if match:
                                    findings.append((path, i, line.strip(), label))
                except (PermissionError, IsADirectoryError, UnicodeDecodeError):
                    pass  # Silently skip unreadable or invalid files
    return findings