def main():
    print("JARVIS-lite is online. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Shutting down.")
            break
        print(f"Jarvis: I heard '{user_input}'")


if __name__ == "__main__":
    main()