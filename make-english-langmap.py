import utils
import re
import sys


SOURCE_LANGMAPPER_H_PATH = "../giada/src/gui/langMapper.h"
SOURCE_LANGMAPPER_CPP_PATH = "../giada/src/gui/langMapper.cpp"
DEST_ENGLISH_LANGMAP_PATH = "../giada-langmaps/langmaps/english.langmap"


def get_langmapper_keys(file_path):
    utils.check_file_existence(file_path)
    with open(file_path, "r") as f:
        content = f.read()
        pattern = re.compile(r'static constexpr auto (\w+)\s*=\s*"([^"]+)"\s*;')
        out = {}
        for match in pattern.finditer(content):
            var_name = match.group(1)
            var_value = match.group(2)
            out[var_name] = var_value
        return out


def get_langmapper_values(file_path, keys):
    utils.check_file_existence(file_path)
    out = []
    with open(file_path, "r") as f:
        content = f.read()
        for key, value in keys.items():
            pattern = rf'm_data\[{key}\]\s*=\s*((?:"(?:[^"\\]|\\.)*"\s*)+);'
            match = re.search(pattern, content, re.MULTILINE)
            if not match:
                print(f"Key {key} not found in {file_path}!")
                sys.exit(1)
            # Extract all quoted parts and join them
            all_strings = re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
            full_text = "".join(all_strings)
            out.append((value, full_text))
    return out


def make_langmap(file_path, values):
    with open(file_path, "w") as f:
        content = "{\n"
        for i, value in enumerate(values):
            is_last = i == len(values) - 1
            comma = "" if is_last else ","
            content += f'\t"{value[0]}": "{value[1]}"{comma}\n'
        content += "}"
        f.write(content)


if __name__ == "__main__":
    keys = get_langmapper_keys(SOURCE_LANGMAPPER_H_PATH)
    values = get_langmapper_values(SOURCE_LANGMAPPER_CPP_PATH, keys)
    make_langmap(DEST_ENGLISH_LANGMAP_PATH, values)
