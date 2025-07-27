import ollama
import time
import os
import sys

MODEL_OLLAMA = "llama3.2"

def chat_with_model(prompt):
    print("Sending to Ollama...")
    start_time = time.time()
    response = ollama.chat(model=MODEL_OLLAMA, messages=[{"role": "user", "content": prompt}])
    reply = response["message"]["content"]
    elapsed = time.time() - start_time
    print(f"Ollama responded in {elapsed:.2f} seconds.")
    return reply

def main():
    print("Text Chat Interface (type 'quit' or CtrlC to exit)\n")
    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit"):
                print("Bye")
                break
            
            bot_reply = chat_with_model(user_input)
            print("Bot:", bot_reply, "\n")
    except (KeyboardInterrupt, EOFError):
        print("\nExiting")
        sys.exit(0)

if __name__ == "__main__":
    main()