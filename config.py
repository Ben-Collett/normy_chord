import config_utils
from evdev import ecodes
keyboard = "/dev/input/event14"
chords: dict = config_utils.load_library("./maps.json")

chords.update({"as": config_utils.backspace()})

just_spaced = config_utils.last_character_entered_equals(' ')
backspace_on_space = config_utils.backspace(conditionals=[just_spaced])
write_suffix = config_utils.write("'ll ")
chords.update({"kl": backspace_on_space.and_then(write_suffix)})
chords.update(
    {"df": config_utils.backspace(conditionals=[just_spaced]).and_then(config_utils.write("'ll "))})


write_parans = config_utils.write("()")
move_cursor_left = config_utils.type_keys([ecodes.KEY_LEFT])
chords.update({"jk": write_parans.and_then(move_cursor_left)})
print(chords)

separator = ' '

"""
chord_detection_delay is the amount of time after a chord is detected before it plays
the reason that this value is needed is if you type the letters in a chord fast enough you may trigger a false positive
this prevents that you generally what the lowest value you can get away with so if you aren't getting any false postives then you can try to lower it
if you are then raise it
if you are using primarily 3+ letter chords you probably don't have to worry about it
or if you are going chord only I suppose it doesn't matter
I recommend doing a couple typing test with monkey type to see which way you need to go

"""
chord_detection_delay = 0.065
