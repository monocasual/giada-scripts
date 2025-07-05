import utils
import re
import sys
import json


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


def get_source_langmap_as_json(h_file_path, cpp_file_path):
    """Turns the h/cpp file combo into a dict object. This is the source of truth
    of the langmap messages."""
    keys = get_langmapper_keys(h_file_path)
    values = get_langmapper_values(cpp_file_path, keys)
    langmap_dict = dict(values)
    return langmap_dict


def make_langmap(file_path, langmap_dict):
    with open(file_path, "w") as f:
        json.dump(langmap_dict, f, indent=4)


if __name__ == "__main__":
    langmap_dict = get_source_langmap_as_json(
        SOURCE_LANGMAPPER_H_PATH, SOURCE_LANGMAPPER_CPP_PATH
    )
    make_langmap(DEST_ENGLISH_LANGMAP_PATH, langmap_dict)
