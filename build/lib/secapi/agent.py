# secapi/agent.py (Natural language input, structured AI command output)

from openai import AzureOpenAI
from secapi.secure import load_key, add_key_interactively, list_keys, delete_key, rotate_key
from secapi.scanner import scan_directory
from secapi.scanner_ai import ai_scan_path

class SecAPIAgent:
    def __init__(self):
        api_key = load_key("azure_api_key")
        endpoint = load_key("azure_endpoint")
        deployment = load_key("azure_deployment")

        self.deployment = deployment
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version="2023-07-01-preview",
            azure_endpoint=endpoint
        )

        self.chat_history = [
            {
                "role": "system",
                "content": (
                    "You are SecAPI Assistant. You interpret natural language and return strict commands only.\n"
                    "Valid commands:\n"
                    "- add\n"
                    "- list\n"
                    "- delete <key>\n"
                    "- rotate <key>\n"
                    "- check <directory>\n"
                    "- ai <file_or_dir>\n"
                    "- exit\n\n"
                    "Return ONLY the command. No explanations. No extra sentences. Examples:\n"
                    "'remove my GitHub token' → 'delete github_key'\n"
                    "'scan the src folder' → 'check src'\n"
                    "'quit' → 'exit'"
                )
            }
        ]

    def interpret_command(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=self.chat_history,
                temperature=0.2,
                max_tokens=150
            )
            reply = response.choices[0].message.content.strip()
            self.chat_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            print(f"❌ AI interpretation failed: {e}")
            return None

    def parse_command(self, reply_text):
        text = reply_text.strip().lower()
        parts = text.split(maxsplit=1)
        if not parts:
            return (None, None)

        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if cmd in {"add", "list", "exit"}:
            return (cmd, None)
        if cmd in {"delete", "rotate", "check", "ai"} and arg:
            return (cmd, arg)

        return (None, None)

    def execute_command(self, command, value=None):
        try:
            if command == "add":
                add_key_interactively()
            elif command == "list":
                list_keys()
            elif command == "delete" and value:
                delete_key(value)
            elif command == "rotate" and value:
                rotate_key(value)
            elif command == "check" and value:
                print(f"\n🔍 Scanning directory: {value}\n")
                findings = scan_directory(value)
                if findings:
                    for idx, (file, line, content, label) in enumerate(findings):
                        print(f"[{idx+1}] {label} in {file} (line {line})")
                else:
                    print("✅ No secrets found.")
            elif command == "ai" and value:
                ai_scan_path(value)
            elif command == "exit":
                print("👋 Goodbye!")
                exit(0)
            else:
                print("❌ Unknown or incomplete command.")
        except Exception as e:
            print(f"❌ Failed to execute command: {e}")

    def run(self):
        print("\n🤖 SecAPI AI Agent is running! Type 'exit' anytime to quit.\n")
        while True:
            try:
                user_input = input("🗒️ What would you like to do? ").strip()
                if not user_input:
                    continue
                ai_reply = self.interpret_command(user_input)
                if not ai_reply:
                    print("❌ AI could not process your request.")
                    continue
                print(f"🧠 AI understood: {ai_reply}")
                command, value = self.parse_command(ai_reply)
                if command:
                    self.execute_command(command, value)
                else:
                    print("❌ Could not parse the AI's reply. Try rephrasing.")
            except KeyboardInterrupt:
                print("\n👋 Exiting. See you next time!")
                break

def run_agent():
    agent = SecAPIAgent()
    agent.run()
