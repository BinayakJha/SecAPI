# 🚀 SecAPI

**Secure, AI-Driven API Key Management & Leak Prevention — Directly from Your Terminal.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](#)
[![Security: AES-256](https://img.shields.io/badge/Security-AES--256-red.svg)](#)
[![Tests: 12/12 Passing](https://img.shields.io/badge/Tests-12%2F12%20Passing-brightgreen.svg)](#)
[![Website: secapi.netlify.app](https://img.shields.io/badge/Website-secapi.netlify.app-10B981.svg)](https://secapi.netlify.app/)

🌐 **Explore the Interactive Showcase**: **[secapi.netlify.app](https://secapi.netlify.app/)**

---

## 📝 Overview

Hardcoding API keys in repository files is one of the leading causes of security leaks. Copying and pasting secrets across environment vaults is slow, and developers often forget to rotate keys.

**SecAPI makes the secure path the fastest path.** It is a lightweight Python CLI utility that secures your development environment in three steps:
1. **Scans** your codebases for exposed keys.
2. **Vaults** secrets locally using strong **AES-256 encryption** derived via **PBKDF2-HMAC**.
3. **Replaces** raw hardcoded strings in your source code with safe, in-memory reference loaders (`load_key("key_name")`)—preserving your variable names and comments.

---

## ✨ Features

* 🔒 **Double-Encrypted local Vault**: Uses PBKDF2-HMAC (100,000 iterations of SHA-256) to derive keys from your master password. No data ever leaves your machine.
* 🔑 **Emergency Recovery Keys**: Generates a 24-character recovery phrase (`XXXX-XXXX-...`) upon initialization. If you forget your password, you can safely reset it without losing keys.
* 🛑 **Automatic Git Pre-commit Hooks**: Protects your codebase. Run `secapi init-hook` to block commits automatically if any unencrypted secrets are introduced.
* 🎨 **Interactive TUI Dashboard**: Running `secapi list` displays an ANSI color-coded status board showing key names, ages, creation dates, and lifecycle statuses (🟢 `Active`, 🟡 `Rotate Soon`, 🔴 `Expired`).
* 👥 **Multi-Environment Profiles**: Route vault profiles (e.g. `dev`, `staging`, `prod`) using `--env` parameters or by setting `export SECAPI_ENV=prod`.
* 🤖 **Smart LHS-Preserving Fixer**: Parses assignments and replaces only the string literal (RHS) of a leak, keeping variable names (LHS) and trailing comments intact.
* 🗣️ **Conversational AI Agent & Audits (Gemini & OpenAI)**: Scan files using on-device AI. Defaults to a zero-dependency **Google Gemini** implementation built with standard library `urllib`, avoiding local package version conflicts.

---

## 🚦 Getting Started

### 1. Installation

#### Option A: One-Command Universal Installer (Recommended)
For an automated, zero-config installation directly from git:
```bash
curl -fsSL https://raw.githubusercontent.com/BinayakJha/SecAPI/main/install.sh | sh
```

#### Option B: Isolated Python Installation via pipx
If you prefer standard Python package isolation:
```bash
pipx install git+https://github.com/BinayakJha/SecAPI.git
```

#### Option C: Manual/Development Setup
Clone the repository and install it locally:
```bash
git clone https://github.com/BinayakJha/SecAPI.git
cd SecAPI
pip install -e .
```

### 2. Configure Your AI Key (Optional)
To use the AI scanner (`secapi ai`) or conversational chatbot (`secapi agent`), configure a Gemini API key:
* **Option A**: Export as an environment variable (recommended):
  ```bash
  export GEMINI_API_KEY="your-gemini-api-key"
  ```
* **Option B**: Store it securely in the vault:
  ```bash
  secapi add
  # Give the key the name: gemini_api_key
  ```

### 3. Run the Step-by-Step Demo
We provide a helper demo to build a mock project containing a hardcoded stripe key:
```bash
python3 demo/demo_workflow.py
```
This script sets up a `./demo_project` folder. You can immediately run:
```bash
secapi check ./demo_project
```
Choose option `[1]` to fix the leak and watch SecAPI vault the key, prompt you to write down your recovery key, and update the source file securely!

---

## 🔧 Command Reference

| Command | Usage | Description |
|---------|-------|-------------|
| `check` | `secapi check <path>` | Scan a file or folder using the regex scanner engine (supports ignores). |
| `add` | `secapi add` | Interactively save a new API credential to the vault. |
| `list` | `secapi list` | Print the color-coded status dashboard of all stored keys. |
| `load` | `secapi load <name>` | Decrypt and load a key value (checks expiration limits). |
| `rotate` | `secapi rotate <name>` | Rotate the secret value for a stored key. |
| `delete` | `secapi delete <name>` | Delete a key from the vault (requires password entry). |
| `recover` | `secapi recover` | Reset your master password using your emergency recovery key. |
| `init-hook` | `secapi init-hook` | Install an automatic Git pre-commit scanner hook in `.git/`. |
| `ai` | `secapi ai <path>` | Scan files for leaks using the AI-powered model scanner. |
| `agent` | `secapi agent` | Launch the conversational NL chatbot executor. |

---

## ⚙️ Configuration (`secapi_config.yaml`)

Configure key lifetimes and model preferences in a `secapi_config.yaml` file in the root of your project:

```yaml
security:
  auto_rotate: true
  rotate_interval_days: 30 # Keys older than this will show 🔴 Expired warnings

ai:
  provider: "gemini" # gemini, openai, or azure
  model: "gemini-1.5-flash"
```

---

## 🧪 Running Tests

We maintain a suite of **11 automated unit tests** verifying directory ignores, regex engines, PBKDF2 encryption, recovery keys, and pre-commit hook setups. Run them using:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/
```

---

## 🤝 Contributing

Pull requests are welcome!
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 🚀

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.
