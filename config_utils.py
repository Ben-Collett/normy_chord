import json
from evdev import ecodes
from action_types import WriteAction, TypeAction, ActionList


def write(input: str, if_conditional=None):
    return ActionList().and_then(WriteAction(input))


def type_keys(key_codes):
    return ActionList().and_then(TypeAction(key_codes))


def backspace():
    return ActionList().and_then(TypeAction([ecodes.KEY_BACKSPACE]))


def just_chorded():
    pass


def last_character_entered_equals(char):
    pass


def exec(char):
    pass


def load_library(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    return data
