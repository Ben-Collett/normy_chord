

def json_to_chords(data):
    result = {}
    for key, value in data.items():
        key_set = frozenset(key)
        result[key_set] = value

    return result
