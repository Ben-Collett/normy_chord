import evdev
import config

from keyboard import EvKeyBoard
import os
import time
import threading
import argparse
import chord_parse
from action_types import WriteAction, TypeAction, ActionList
from conditionals import Conditional, LastCharTyped
from config_utils import load_library


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


print('parsing cords')
if config.chords:
    chords = chord_parse.json_to_chords(config.chords)
else:
    chords = load_library(config.chord_library_path)
    chords = chord_parse.parse_library_flat_json(chords)
print('finished parsing chords')


def exit_condition():
    escape_down = ecodes.KEY_ESC in keyboard.down_letters
    modifiers_down = keyboard.control_down and keyboard.alt_down and keyboard.shift_down
    if modifiers_down and escape_down:
        exit()


def _eval_conditions(conditionals: [Conditional]):
    for conditional in conditionals:
        if isinstance(conditional, LastCharTyped):
            if keyboard.last_key_entered() != conditional.char_to_check:
                return False

    return True


def _handle_actions(actions: ActionList):
    for action in actions:
        if len(action.conditionals) != 0:
            time.sleep(0.1)
        if not _eval_conditions(action.conditionals):
            continue

        if isinstance(action, WriteAction):
            keyboard.write(action.data)
        elif isinstance(action, TypeAction):
            keyboard.type_key_codes(action.key_codes)


try:
    while True:
        keys_snapshot = keyboard.get_down_letters()
        if keys_snapshot in chords:
            chord = chords[keys_snapshot]
            time.sleep(config.chord_detection_delay)
            key_snapshot2 = keyboard.get_down_letters()
            if key_snapshot2 == keys_snapshot:
                keyboard.backspace(x_times=len(keys_snapshot))
                if type(chord) is str:
                    keyboard.write(chord+config.separator)
                else:
                    _handle_actions(chord)
        if exit_condition():
            exit(0)

except KeyboardInterrupt:
    print("Exiting...")
