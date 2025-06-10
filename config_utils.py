import json
from evdev import ecodes
from action_types import WriteAction, TypeAction, ActionList
from conditionals import LastCharTyped


def write(input: str, if_conditional=None):
    return ActionList().and_then(WriteAction(input))


def type_keys(key_codes):
    return ActionList().and_then(TypeAction(key_codes))


def backspace(conditionals=[]):
    return ActionList().and_then(TypeAction([ecodes.KEY_BACKSPACE], conditionals))


def last_character_entered_equals(char):
    return LastCharTyped(char)


def exec(char):
    pass


def load_library(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data
