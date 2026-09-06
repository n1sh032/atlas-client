# just the main loop now, everything else moved into its own file.
# see design.md for why its split up this way

import time

from voice import listen_for_wakeword, listen_for_command, speak
from assistant import talk_to_atlas_safe, save_history


def main():
    print("atlas is online (voice mode)")
    while True:
        try:
            listen_for_wakeword()
            cmd = listen_for_command()
        except KeyboardInterrupt:
            print("shutting down")
            save_history()
            break
        except Exception as e:
            print(f"atlas: listening broke ({e}), trying again")
            time.sleep(2)
            continue

        if not cmd:
            continue

        if cmd.strip().lower() == "exit":
            print("shutting down")
            save_history()
            break

        reply = talk_to_atlas_safe(cmd)
        speak(reply)


if __name__ == "__main__":
    main()