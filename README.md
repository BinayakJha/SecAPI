# 🚀 SecAPI  
**Secure, AI-Driven API Key Management in Your Terminal**

---

## 📝 What Is SecAPI?  
SecAPI is a Python CLI tool that helps you **store**, **rotate**, and **audit** your API keys and secrets—**all with natural-language commands**. No more hunting through vault UIs or hand-rolling encryption: SecAPI keeps your keys safe, automates rotation, and logs every action for full compliance.

---

## ✨ Key Features

- **Instant Control**  
  One-line CLI or plain-English commands for adding, listing, rotating, and deleting keys.

- **Ironclad Security**  
  AES-256 encryption for keys at rest and in transit—everything happens locally; your secrets never leave your machine.

- **AI-Powered Scanning**  
  Scan files and directories for hardcoded credentials using an on-device AI agent.

- **Natural Language Agent**  
  Talk to SecAPI like a chatbot: “rotate my Stripe key” → SecAPI does the rest.

- **Total Auditability**  
  Immutable, append-only logs record who did what and when. Easily plug into Azure Key Vault, AWS Secrets Manager, or any vault you like.

---

## 🛠️ Quickstart

### Prerequisites  
- Python 3.7+  
- pip  

### Install  
```bash
pip install secapi
```

### First Run  
Open your terminal and type:
```bash
secapi -h
```
You’ll see all available commands.

---

## 🚦 Common Commands

| Command                       | What It Does                                    | Example                                  |
|-------------------------------|-------------------------------------------------|------------------------------------------|
| `secapi add`                  | Securely add a new key interactively            | `secapi add`                             |
| `secapi list`                 | Show all stored keys                            | `secapi list`                            |
| `secapi rotate <key-name>`    | Rotate a key and update vault                   | `secapi rotate stripe_api_key`           |
| `secapi delete <key-name>`    | Remove a key from the vault                     | `secapi delete old_api_key`              |
| `secapi load <key-name>`      | Load a key into your shell environment          | `secapi load prod_db_key`                |
| `secapi check <path>`         | Scan code for exposed secrets via AI            | `secapi check ./src`                     |
| `secapi agent`                | Launch the AI chatbot for natural-language ops   | `secapi agent`                           |

---

## ⚙️ Configuration

Create a `secapi_config.yaml` in your project root:

```yaml
security:
  auto_rotate: true          # turn on/off automated rotation
  rotate_interval_days: 30   # how often to auto-rotate
  encryption_key: YOUR_KEY   # your master encryption key
```

---

## 🔍 How It Works

1. **You ask** (CLI or plain English).  
2. **Agent parses** your intent & entities.  
3. **Secure engine** performs AES-256 encryption/decryption & CRUD.  
4. **Vault** stores keys in an encrypted SQLite DB.  
5. **Audit trail** logs every action in an append-only file.

---

## 🤝 Contributing

We welcome bug fixes, docs improvements, or new features:

1. Fork the repo  
2. Create a feature branch  
3. Commit & push your changes  
4. Open a Pull Request  

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

Happy securing! 🔐
