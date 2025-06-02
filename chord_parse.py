import json


def parse_library_flat_json(json_file_path):
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    result = {}
    for key, value in data.items():
        key_set = frozenset(key)
        result[key_set] = value

    return result
