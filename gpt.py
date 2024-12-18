import os
from openai import OpenAI

# Set up OpenAI API key
OpenAI.api_key = os.getenv("OPENAI_API_KEY")


def load_required_memory_from_folder(folder_path, required_files):
    """
    Loads only the required .txt files from a folder and concatenates their contents.
    """
    memory = ""
    try:
        for filename in required_files:
            file_path = os.path.join(folder_path, filename)
            if filename.endswith(".txt") and os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    memory += f"\n{file.read()}\n"
    except Exception as e:
        print(f"Error loading memory: {e}")
    return memory


def save_conversation_to_file(file_path, conversation):
    """
    Appends the conversation to a text file.
    """
    with open(file_path, "a", encoding="utf-8") as file:
        file.write(conversation + "\n")


def trim_memory(memory, max_tokens=3000):
    """
    Trims the memory to stay within a token limit by keeping recent messages.
    """
    memory_tokens = memory.split("\n")
    while len(" ".join(memory_tokens)) > max_tokens:
        memory_tokens.pop(0)  # Remove oldest messages
    return "\n".join(memory_tokens)


def generate_response(prompt, rules, memory):
    """
    Sends a prompt, rules, and memory to GPT-4 and returns the response.
    """
    system_message = f"Your personality and rules are as follows: {rules}\n"
    memory_message = f"You have the following memory:\n{memory}\n"
    
    messages = [
        {"role": "system", "content": system_message + memory_message},
        {"role": "user", "content": prompt}
    ]
    
    try:
        # Instantiate the OpenAI client
        client = OpenAI(api_key=OpenAI.api_key)
        
        # Generate response using the new API method
        response = client.chat.completions.create(
            model="gpt-4",  # Change to "gpt-4-turbo" if using that model
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {e}"


# Example Usage
if __name__ == "__main__":
    # Define the personality and rules
    rules = """
    - You are a Programming Teacher at Moorestown High School.
    - You are named Brian Orak but are known as Mr. Orak.
    - You have a very short temper and are known for your sarcasm.
    - You hate vegetables as you are not a rabbit.
    - You LOVE Taylor Swift and her music.
    - When someone says that they need help, you say "Mouse" right before saying what's wrong.
    - You are usually very monotone and don't show much emotion.
    - Some phrases you say are "We get work done here".
    - You don't like to be called Brian.
    - You stick to the subject at hand and don't bring up random topics.
    - You are very strict with your students.
    - You can be nice, but you are usually very strict.
    - You are very sarcastic.
    - You are very monotone.
    - All of your coding knowledge is from your memory.
    """

    # Load only the required memory files
    memory_folder = "memory_files"  # Change this to your folder path
    required_files = ["file1.txt", "file2.txt"]  # List the specific files you want to load
    memory = load_required_memory_from_folder(memory_folder, required_files)
    memory = trim_memory(memory)  # Trim the memory to stay within token limits
    memory_file = "conversation_memory.txt"

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Chatbot: Goodbye!")
            break

        chatbot_response = generate_response(user_input, rules, memory)
        print(f"Chatbot: {chatbot_response}")

        # Update memory
        conversation = f"User: {user_input}\nChatbot: {chatbot_response}"
        memory += conversation + "\n"
        memory = trim_memory(memory)  # Trim after each conversation
        save_conversation_to_file(memory_file, conversation)
