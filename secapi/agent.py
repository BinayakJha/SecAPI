import openai
from secapi.cli import main as cli_main

# Load your OpenAI API key securely
from secapi.secure import load_key

openai.api_key = load_key("openai_api_key")


def interpret_command(user_input):
    """
    Use OpenAI's GPT model to interpret the user's natural language input
    and map it to a specific CLI command.
    """
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Use a GPT model
            prompt=f"""
            You are an assistant for a security tool called SecAPI. Map the following user input to a CLI command:
            User Input: "{user_input}"
            CLI Commands:
            - check <directory>
            - list
            - delete <key_name>
            - rotate <key_name>
            - load <key_name>
            - ai <path>
            - add
            - export <file>
            - import <file>
            - scan <file>
            - help
            Output the exact CLI command without explanation.
            """,
            max_tokens=100,
            temperature=0.2,
        )
        command = response.choices[0].text.strip()
        return command
    except Exception as e:
        print(f"❌ Failed to interpret command: {e}")
        return None


def run_agent():
    """
    Run the AI agent to interpret user input and execute the corresponding command.
    """
    print("🤖 SecAPI AI Agent is now running. Type 'exit' to quit.")
    while True:
        user_input = input("🗒️ What would you like to do? ").strip()
        if user_input.lower() == "exit":
            print("👋 Goodbye!")
            break

        command = interpret_command(user_input)
        if command:
            print(f"🔧 Interpreted Command: {command}")
            try:
                # Simulate running the CLI command
                cli_args = command.split()
                cli_main(cli_args)
            except SystemExit:
                # Catch SystemExit to prevent the program from exiting
                pass
        else:
            print("❌ Sorry, I couldn't understand your request.")