import evdev
import config

from keyboard import EvKeyBoard
import os
import time
import threading
import argparse
import chord_parse


def kill_after_delay(delay):
    time.sleep(delay)
    print(f"Killing process {os.getpid()} after {delay} seconds")
    os._exit(1)  # Force exit the current process


parser = argparse.ArgumentParser(
    description="Optional kill_after_delay runner.")
parser.add_argument(
    '-t', type=int, help="kills the program in t=n seconds"
)

args = parser.parse_args()

if args.t is not None:
    # Start the thread with the provided delay
    killer_thread = threading.Thread(
        target=kill_after_delay, args=(args.t,))
    killer_thread.daemon = True
    killer_thread.start()


ecodes = evdev.ecodes

hardware_keyboard = evdev.InputDevice(config.keyboard)
output_keyboard = evdev.UInput(name='chording writing keyboard')

keyboard = EvKeyBoard(hardware_keyboard)


print(f'loading library {config.chord_library_path}')
chords = chord_parse.parse_library_flat_json(config.chord_library_path)
print(f'loaded library {config.chord_library_path}')


def exit_condition():
    escape_down = ecodes.KEY_ESC in keyboard.down_letters
    modifiers_down = keyboard.control_down and keyboard.alt_down and keyboard.shift_down
    if modifiers_down and escape_down:
        exit()


try:
    while True:
        keys_snapshot = keyboard.get_down_letters()
        if keys_snapshot in chords:
            chord = chords[keys_snapshot]
            keyboard.backspace(x_times=len(keys_snapshot))
            keyboard.write(chord+config.separator)
        if exit_condition():
            exit(0)

except KeyboardInterrupt:
    print("Exiting...")
