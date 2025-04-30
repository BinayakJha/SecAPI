# **SecAPI: Secure Your API Keys Before They Leak**

## **Overview**
SecAPI is a Python-based tool designed to help developers securely manage and store API keys, credentials, and sensitive information. It offers automated key rotation, end-to-end encryption, AI-powered scanning, and a natural language agent to simplify key management. Whether you're working on a personal project, a startup, or managing large-scale enterprise-level applications, SecAPI provides a straightforward and secure solution for API key management.

---

## **Features**
- **Secure API Key Management**: Safeguard your keys with encryption both at rest and in transit.
- **Automated Key Rotation**: Automatically rotate your API keys to minimize exposure risks.
- **AI-Powered Security**: Use AI to scan your codebase for hardcoded secrets and vulnerabilities.
- **Natural Language Agent**: Interact with SecAPI using natural language commands for seamless key management.
- **Easy CLI Interface**: Manage your keys with simple commands for checking, rotating, listing, and deleting keys.
- **Comprehensive Auditing**: Keep track of all key access events for full transparency and compliance.
- **Azure Integration**: Supports Azure OpenAI for natural language processing and secure key management.

---

## **Installation**

### **Prerequisites**
- Python 3.6 or later
- pip (Python package manager)

### **Installation via pip**
To install SecAPI as a Python package, simply run the following command:
```bash
pip install secapi
```

This will install the latest version of SecAPI and its dependencies.

---

## **Usage**

### **Command-Line Interface (CLI)**
SecAPI is operated through a command-line interface (CLI). After installing, you can run the tool by typing `secapi` followed by the desired command.

To get started, you can check the available commands:
```bash
secapi -h
```

### **Commands**

1. **`check <dir>`**:
   - Scans the given directory for any unprotected API keys or sensitive data.
   - **Example**:  
     ```bash
     secapi check /path/to/project
     ```

2. **`list`**:
   - Lists all stored API keys in your SecAPI vault.
   - **Example**:  
     ```bash
     secapi list
     ```

3. **`delete <key_name>`**:
   - Deletes a specific API key from the vault.
   - **Example**:  
     ```bash
     secapi delete my-api-key
     ```

4. **`rotate <key_name>`**:
   - Rotates the specified API key and updates it in the vault.
   - **Example**:  
     ```bash
     secapi rotate my-api-key
     ```

5. **`load <key_name>`**:
   - Loads a specific API key for use in the application.
   - **Example**:  
     ```bash
     secapi load my-api-key
     ```

6. **`ai <file_or_dir>`**:
   - Uses AI to scan a file or directory for hardcoded secrets and vulnerabilities.
   - **Example**:  
     ```bash
     secapi ai /path/to/file_or_dir
     ```

7. **`add`**:
   - Adds a new API key to the vault interactively.
   - **Example**:  
     ```bash
     secapi add
     ```

8. **`agent`**:
   - Launches the AI-powered natural language agent for managing keys and scanning projects.
   - **Example**:  
     ```bash
     secapi agent
     ```

---

### **Natural Language Agent**
The SecAPI agent allows you to interact with the tool using natural language commands. Simply type what you want to do, and the agent will interpret and execute the appropriate command.

#### **Example Interaction**:
```bash
secapi agent
```
```
🤖 SecAPI AI Agent is now running. Type 'exit' to quit.
🗒️ What would you like to do? add a new API key
🔧 Executing: add
🆕 Add a New API Key
Give this key a name (e.g., 'openai_key'): openai_key
🔑 Enter your API key: ********
✅ Key 'openai_key' securely stored in your vault.
```

---

## **Configuration**

To configure SecAPI, simply create a configuration file called `secapi_config.yaml` in your project directory. Here, you can define security settings, like the frequency of key rotation, and specify encryption options.

**Example `secapi_config.yaml`:**
```yaml
security:
  auto_rotate_keys: true
  rotate_interval_days: 30
  encryption_key: YOUR_ENCRYPTION_KEY
```

---

## **How It Works**

1. **Key Rotation**: SecAPI automatically rotates your API keys to ensure they are always up-to-date and secure. When you use the `rotate` command, it generates a new key, replaces the old one, and securely updates it in the system.
2. **Encryption**: SecAPI uses industry-standard encryption to protect stored keys. It ensures that keys are never exposed in plaintext, both in storage and during transmission.
3. **AI-Powered Scanning**: SecAPI scans your project directories for exposed keys and sensitive data, making it easier to spot potential vulnerabilities.
4. **Natural Language Agent**: The AI-powered agent interprets natural language commands and maps them to SecAPI CLI commands for seamless interaction.
5. **Auditing**: SecAPI logs all actions performed on your keys, such as creation, modification, deletion, and access, ensuring compliance and traceability.
6. **Azure Integration**: SecAPI supports Azure OpenAI for natural language processing, enabling secure and scalable AI-powered features.

---

## **Contributing**

We welcome contributions to SecAPI! Whether you're fixing bugs, improving documentation, or adding new features, we appreciate your input.

### **How to Contribute**
1. **Fork the repository**:  
   Create a fork of the repository to work on your changes.
   
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/secapi.git
   ```

3. **Create a branch**:
   ```bash
   git checkout -b feature-branch
   ```

4. **Make your changes**:  
   Implement your changes, add tests if necessary, and ensure the code works properly.

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

6. **Push your changes**:
   ```bash
   git push origin feature-branch
   ```

7. **Create a pull request**:  
   Once you're done, create a pull request with a description of your changes.

### **Code of Conduct**
Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) when contributing to this project.

---

## **License**
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## **Contact**
For any questions or support, feel free to open an issue or contact us at [email@example.com].

---

### **Acknowledgments**
- **Thanks to the open-source community** for their contributions to tools and libraries that power SecAPI.
- **Azure OpenAI** for enabling natural language processing capabilities.
