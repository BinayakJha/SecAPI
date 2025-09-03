# 🚀 SecAPI  
**Secure, AI-Driven API Key Management — From Your Terminal**  

---

## 🎥 Demo Video  
See SecAPI in action:  
<p align="center">  
  <a href="https://www.youtube.com/watch?v=2Up_qoX97FA" target="_blank">  
    <img src="https://img.youtube.com/vi/2Up_qoX97FA/maxresdefault.jpg" alt="SecAPI Demo" width="600"/>  
  </a>  
</p>  

---

## 📝 Overview  

Managing API keys is one of the most frustrating and error-prone parts of development. Teams either:  
- Hard-code keys into repos 🫠  
- Copy-paste across vaults and dashboards 🔑  
- Forget to rotate until it’s too late 🚨  

**SecAPI fixes this.** It’s a lightweight Python CLI that makes the **secure path the fastest path**:  
- Store keys locally with AES-256 encryption.  
- Rotate keys instantly with one command or a plain-English prompt.  
- Scan repos for hardcoded secrets using an on-device AI agent.  
- Keep a full, immutable audit trail for compliance.  

---

## ✨ Features  

- ⚡ **Instant Control** — Manage keys with one-line CLI or natural language.  
- 🔒 **Ironclad Security** — AES-256 everywhere, fully local, nothing leaves your machine.  
- 🤖 **AI-Powered Scanning** — Catch hardcoded secrets before they leak.  
- 🗣️ **Natural Language Agent** — “Rotate my Stripe key” → SecAPI does it.  
- 🧾 **Total Auditability** — Append-only logs for full transparency.  
- ☁️ **Vault-Ready** — Optional adapters for AWS Secrets Manager, Azure Key Vault.  

---

## 🚦 Quickstart  

### Prerequisites  
- Python 3.7+  
- pip  

### Install  
```bash
pip install secapi
```

### First Run  
```bash
secapi -h
```

---

## 🔧 Common Commands  

| Command | What It Does | Example |  
|---------|--------------|---------|  
| `secapi add` | Securely add a new key interactively | `secapi add` |  
| `secapi list` | Show all stored keys | `secapi list` |  
| `secapi rotate <key>` | Rotate a key & update vault | `secapi rotate stripe_api_key` |  
| `secapi delete <key>` | Remove a key from the vault | `secapi delete old_api_key` |  
| `secapi load <key>` | Load a key into your shell env | `secapi load prod_db_key` |  
| `secapi check <path>` | AI scan for exposed secrets | `secapi check ./src` |  
| `secapi agent` | Launch chatbot for NL ops | `secapi agent` |  

---

## ⚙️ Configuration  

Create a `secapi_config.yaml` in your project root:  

```yaml
security:
  auto_rotate: true
  rotate_interval_days: 30
  encryption_key: YOUR_MASTER_KEY
```

---

## 🔍 How It Works  

1. **You ask** — via CLI or plain English.  
2. **NL agent parses** intent & entities.  
3. **Secure engine** encrypts/decrypts with AES-256.  
4. **Vault** stores keys in encrypted SQLite.  
5. **Audit trail** appends every action with timestamp.  

---

## 👥 Team & Contribution  

- 💡 Idea + Product Lead: **Binayak Jha**  
- 👨‍👩‍👦 Team: 5 collaborators (design, testing, adoption feedback)  
- 🛠️ My Role: Spearheaded the concept, wrote core CLI, crypto, AI parser, file scanner, audit log, and demo.  

---

## 📊 Why It Matters  

- Developers save time: rotations drop from minutes to seconds.  
- Security teams gain confidence: immutable logs + zero cloud exposure.  
- AI agent lowers friction: developers actually follow best practices.  

> 🏆 Key Insight: **Security only wins when it’s faster than bad habits.**  

---

## 🤝 Contributing  

Pull requests are welcome:  
1. Fork the repo  
2. Create a feature branch  
3. Commit & push  
4. Open a PR 🎉  

---

## 📄 License  

MIT License — see [LICENSE](LICENSE).  

---

🔥 **SecAPI makes security effortless — so teams actually use it.** 🔐  
