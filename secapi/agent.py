# secapi/agent.py (AI-powered command executor + conversational assistant)

from secapi.secure import load_key, add_key_interactively, list_keys, delete_key, rotate_key
from secapi.scanner import scan_directory
from secapi.scanner_ai import ai_scan_path
from secapi.config import get_ai_config
from secapi.gemini import call_gemini

class SecAPIAgent:
    def __init__(self):
        ai_config = get_ai_config()
        self.provider = ai_config["provider"]
        self.model = ai_config["model"]
        self.api_key = ai_config["api_key"]
        self.endpoint = ai_config["endpoint"]

        if not self.api_key:
            print("❌ Warning: AI API key not found in config, env, or vault.")
            print("Please set your API key in secapi_config.yaml or environment variables.")
            exit(1)

        if self.provider == "gemini":
            self.client = None
        elif self.provider == "azure":
            try:
                from openai import AzureOpenAI
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    api_version="2023-07-01-preview",
                    azure_endpoint=self.endpoint
                )
            except ImportError:
                print("❌ Error: The 'openai' library is missing or outdated.")
                print("Please upgrade it using: pip install --upgrade openai")
                exit(1)
        else:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.endpoint
                )
            except ImportError:
                print("❌ Error: The 'openai' library is missing or outdated.")
                print("Please upgrade it using: pip install --upgrade openai")
                exit(1)

        self.chat_history = [
            {
                "role": "system",
                "content": (
                    "You are SecAPI Assistant. You help users securely manage their API keys, scan projects, and answer related programming or pip questions.\n"
                    "If the user gives a task (e.g., 'add key', 'delete openai_key', 'scan'), respond with only the exact command like:\n"
                    "- add\n- list\n- delete <key>\n- rotate <key>\n- check <directory>\n- ai <file_or_dir>\n- exit\n"
                    "If the user is asking a question about this tool, pip usage, programming, or says hello, respond naturally and helpfully.\n"
                    "Never mix a command with an explanation. Either respond with a command or a full sentence."
                )
            }
        ]

    def interpret_command(self, user_input):
        self.chat_history.append({"role": "user", "content": user_input})
        try:
            if self.provider == "gemini":
                sys_instruction = self.chat_history[0]["content"]
                messages = self.chat_history[1:]
                reply = call_gemini(
                    system_instruction=sys_instruction,
                    messages=messages,
                    model=self.model,
                    api_key=self.api_key
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.chat_history,
                    temperature=0.3,
                    max_tokens=300
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

        return ("chat", reply_text)  # Treat as conversational response

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
            elif command == "chat" and value:
                print(f"💬 {value}")
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
                command, value = self.parse_command(ai_reply)
                self.execute_command(command, value)
            except KeyboardInterrupt:
                print("\n👋 Exiting. See you next time!")
                break

def run_agent():
    agent = SecAPIAgent()
    agent.run()
