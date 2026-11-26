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

        elif cmd == "open downloads":
            dl_path = os.path.join(os.path.expanduser("~"), "Downloads")
            os.startfile(dl_path)
            print("Atlas: opening downloads folder")

        else:
            print("Atlas: not sure of that command yet")

main()