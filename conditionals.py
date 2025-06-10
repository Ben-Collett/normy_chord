class Conditional:
    pass


class LastCharTyped:
    def __init__(self, last_char):
        self.char_to_check = last_char

    def eval(key_buffer, chord_length):
        return key_buffer[-chord_length]
