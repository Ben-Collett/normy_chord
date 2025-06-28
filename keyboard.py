import threading
import evdev
import string
from utils.ring_buffer import RingBuffer
_ecodes = evdev.ecodes

_alphabet = frozenset(string.ascii_lowercase)
_modifiers = {
    _ecodes.KEY_LEFTCTRL,
    _ecodes.KEY_RIGHTCTRL,
    _ecodes.KEY_LEFTSHIFT,
    _ecodes.KEY_RIGHTSHIFT,
    _ecodes.KEY_LEFTALT,
    _ecodes.KEY_RIGHTALT,
    _ecodes.KEY_LEFTMETA,
    _ecodes.KEY_RIGHTMETA,
    _ecodes.KEY_FN  # might not be on all keyboards
}
_uppercase = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_")
_char_to_key = {
    'a': _ecodes.KEY_A, 'b': _ecodes.KEY_B, 'c': _ecodes.KEY_C, 'd': _ecodes.KEY_D,
    'e': _ecodes.KEY_E, 'f': _ecodes.KEY_F, 'g': _ecodes.KEY_G, 'h': _ecodes.KEY_H,
    'i': _ecodes.KEY_I, 'j': _ecodes.KEY_J, 'k': _ecodes.KEY_K, 'l': _ecodes.KEY_L,
    'm': _ecodes.KEY_M, 'n': _ecodes.KEY_N, 'o': _ecodes.KEY_O, 'p': _ecodes.KEY_P,
    'q': _ecodes.KEY_Q, 'r': _ecodes.KEY_R, 's': _ecodes.KEY_S, 't': _ecodes.KEY_T,
    'u': _ecodes.KEY_U, 'v': _ecodes.KEY_V, 'w': _ecodes.KEY_W, 'x': _ecodes.KEY_X,
    'y': _ecodes.KEY_Y, 'z': _ecodes.KEY_Z,
    '0': _ecodes.KEY_0, '1': _ecodes.KEY_1, '2': _ecodes.KEY_2, '3': _ecodes.KEY_3,
    '4': _ecodes.KEY_4, '5': _ecodes.KEY_5, '6': _ecodes.KEY_6, '7': _ecodes.KEY_7,
    '8': _ecodes.KEY_8, '9': _ecodes.KEY_9, '_': _ecodes.KEY_MINUS,
    ' ': _ecodes.KEY_SPACE, "'": _ecodes.KEY_APOSTROPHE,
    '\n': _ecodes.KEY_ENTER
}

_key_to_char = {v: k for k, v in _char_to_key.items()}


class EvKeyBoard:
    def __init__(self, keyboard, letter_buffer_size=50):
        self.down_letters = set()
        self.down_keys = set()
        self.meta_down = False
        self.alt_down = False
        self.shift_down = False
        self.control_down = False
        self.fn_down = False
        self.keyboard = keyboard
        self._writing = False
        self.letter_buffer = RingBuffer(letter_buffer_size)
        listener_thread = threading.Thread(
            target=self.listen_keyboard, daemon=True)
        listener_thread.start()

    def backspace(self, x_times=1):
        self._writing = True
        for i in range(0, x_times):
            self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_BACKSPACE, 1)
            self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_BACKSPACE, 0)
        self.keyboard.syn()
        self._writing = False

    def last_key_entered(self):
        return self.letter_buffer.get_last()

    def type_key_codes(self, key_codes):
        self._writing = True

        self.down_letters.clear()

        for key in key_codes:
            # release if already held
            self.keyboard.write(_ecodes.EV_KEY, key, 0)
            self.keyboard.write(_ecodes.EV_KEY, key, 1)
            self.keyboard.write(_ecodes.EV_KEY, key, 0)
        self.keyboard.syn()
        self._writing = False

    def write(self, text: str):
        self._writing = True
        letters = frozenset(self.down_letters)
        self.down_letters.clear()

        for letter in letters:
            key = _char_to_key.get(letter.lower())
            self.keyboard.write(_ecodes.EV_KEY, key, 0)

        for char in text:
            is_upper = char in _uppercase
            key = _char_to_key.get(char.lower())

            if key is None:
                print(f"Unsupported character: {char}")
                continue

            if is_upper:
                self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_LEFTSHIFT, 1)

            self.keyboard.write(_ecodes.EV_KEY, key, 1)  # Key down
            self.keyboard.write(_ecodes.EV_KEY, key, 0)  # Key up
            if is_upper:
                self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_LEFTSHIFT, 0)
            self.keyboard.syn()
        self._writing = False

    def hold_shift(self):
        self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_LEFTSHIFT, 1)

    def release_shift(self):
        self.keyboard.write(_ecodes.EV_KEY, _ecodes.KEY_LEFTSHIFT, 0)

    def _add_if_letter(self, key_code):
        letter = self._get_letter(key_code)
        if letter in _alphabet:
            self.down_letters.add(letter)

    def discard_if_letter(self, key_code):
        letter = self._get_letter(key_code)
        self.down_letters.discard(letter)

    def _get_letter(self, key_code):
        letter = key_code.removeprefix('KEY_').lower()
        if letter in _alphabet:
            return letter
        return None

    def _set_if_modifier(self, key_code):
        e = _ecodes
        if key_code in _modifiers:
            self.meta_down = key_code in (e.KEY_LEFTMETA, e.KEY_RIGHTMETA)
            self.shift_down = key_code in (e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT)
            self.alt_down = key_code in (e.KEY_LEFTALT, e.KEY_RIGHTALT)
            self.fn_down = key_code == e.KEY_FN

    def _unset_if_modifier(self, key_code):
        e = _ecodes
        if key_code in _modifiers:
            left_shift = e.KEY_LEFTSHIFT
            self.meta_down = key_code not in (e.KEY_LEFTMETA, e.KEY_RIGHTMETA)
            self.shift_down = key_code not in (left_shift, e.KEY_RIGHTSHIFT)
            self.alt_down = key_code not in (e.KEY_LEFTALT, e.KEY_RIGHTALT)
            self.fn_down = key_code != e.KEY_FN

    def update_key_buffer(self, event):
        is_typabile_code = event.code in _key_to_char.keys()
        key_down = event.value == 1
        if key_down and is_typabile_code and _key_to_char[event.code] in _alphabet:
            char: str = _key_to_char[event.code]
            if self.shift_down:
                char = char.upper()
            self.letter_buffer.add(char)
        elif event.code == _ecodes.KEY_SPACE and key_down:
            self.letter_buffer.add(' ')
        elif key_down and event.code == _ecodes.KEY_BACKSPACE:
            self.letter_buffer.remove_last()

    def listen_keyboard(self):
        for event in self.keyboard.read_loop():
            self.update_key_buffer(event)

            if event.type == _ecodes.EV_KEY and not self._writing:
                key_code = _ecodes.KEY[event.code]
                if event.value == 1:  # Key press
                    self._add_if_letter(key_code)
                    self._set_if_modifier(key_code)
                    self.down_keys.add(key_code)
                elif event.value == 0:  # Key release
                    self.discard_if_letter(key_code)
                    self._unset_if_modifier(key_code)
                    self.down_keys.discard(key_code)

    def get_down_letters(self):
        return frozenset(self.down_letters)
