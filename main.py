import os
import subprocess

def main():
    print("atlas is online. type exit to quit")
    while True:
        cmd = input("You: ").strip().lower()

        if cmd == "exit":
            print("shutting down")
            break


if __name__ == "__main__":
    main()