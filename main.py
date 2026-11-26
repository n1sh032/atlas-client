import os
import subprocess

def main():
    print("atlas is online. type exit to quit")
    while True:
        cmd = input("You: ").strip().lower()

        if cmd == "exit":
            print("shutting down")
            break

        elif cmd == "open notepad":
            subprocess.Popen(["notepad.exe"])
            print("Atlas: opening notepad")

if __name__ == "__main__":
    main()