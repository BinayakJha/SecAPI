import openai
import os
from secapi.secure import load_key, add_key_interactively, list_keys

class SecAPIAgent:
    def __init__(self):
        # Load the OpenAI API key securely
        openai.api_key = load_key("openai_api_key")
        self.command_map = {
            "add": "add",
            "add api": "add",
            "add api key": "add",
            "add key": "add",
            "check": "check",
            "scan": "check",
            "list": "list",
            "show keys": "list",
            "delete": "delete",
            "remove": "delete",
            "rotate": "rotate",
            "renew": "rotate",
            "load": "load",
            "get": "load",
            "ai": "ai",
            "analyze": "ai",
            "help": "help",
            "exit": "exit"
        }

    def interpret_command(self, user_input):
        """Interpret natural language commands using both direct mapping and OpenAI"""
        # First try direct mapping
        normalized_input = user_input.lower().strip()
        if normalized_input in self.command_map:
            return self.command_map[normalized_input]
        
        # Fall back to OpenAI for more complex queries
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                        You are a command interpreter for SecAPI. Only respond with one of these exact commands:
                        add, check <dir>, list, delete <key>, rotate <key>, load <key>, ai <path>, help, exit
                        Example inputs and outputs:
                        Input: "I need to add a new API key" → Output: "add"
                        Input: "scan my src folder" → Output: "check src"
                        Input: "show me all keys" → Output: "list"
                    """},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.1,
                max_tokens=50
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"❌ Failed to interpret command: {e}")
            return None

    def run(self):
        print("🤖 SecAPI AI Agent is now running. Type 'exit' to quit.")
        while True:
            user_input = input("🗒️ What would you like to do? ").strip()
            if not user_input:
                continue
                
            command = self.interpret_command(user_input)
            
            if command == "exit":
                print("👋 Goodbye!")
                break
            elif not command:
                print("❌ Sorry, I couldn't understand your request.")
            else:
                print(f"🔧 Executing: {command}")
                if command == "add":
                    add_key_interactively()
                elif command.startswith("check"):
                    path = command[5:].strip()
                    if path:
                        print(f"Would scan directory: {path}")
                    else:
                        print("❌ Please specify a directory to check")
                elif command == "list":
                    list_keys()
                else:
                    print(f"ℹ️ Command '{command}' would be executed here")