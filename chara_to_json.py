import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '-t', type=int, help="kills the program in t=n seconds"
)

args = parser.parse_args()
with open(json_file_path, 'r') as f:
    data = json.load(f)

result = {}
for key, value in data.items():
    key_set = frozenset(key)
    result[key_set] = value

return resultpv
