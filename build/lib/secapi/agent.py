import openai
from secapi.secure import load_key

def interpret_command(user_input):
    """
    Use OpenAI's GPT model to interpret the user's natural language input
    and map it to a specific CLI command.
    """
    try:
        # Load the API key securely
 # Replace with your OpenAI API key or load it securely

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use the latest GPT model
            messages=[
                {"role": "system", "content": """
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
                """},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
            max_tokens=100
        )
        command = response['choices'][0]['message']['content'].strip()
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
            # Here you can map the command to your CLI or other logic
        else:
            print("❌ Sorry, I couldn't understand your request.")