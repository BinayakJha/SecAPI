# Regex-based scanner

import os
import re

# Common API key patterns
PATTERNS = {
    "Stripe": r"sk_live_[0-9a-zA-Z]{24,}",
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

def scan_directory(directory):
    findings = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.env', '.json', '.yml', '.yaml', '.txt')):
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