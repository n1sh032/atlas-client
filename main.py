import os
import subprocess

def main():
    print("atlas is online. type exit to quit")
    while True:
        cmd = input("You: ").strip().lower()

        if cmd == "exit":
            break
        print(f"Jarvis: I heard '{user_input}'")


if __name__ == "__main__":
    main()