import utils
import re
import sys
import json
import pathlib


SOURCE_LANGMAPPER_H_PATH = "../giada/src/gui/langMapper.h"
SOURCE_LANGMAPPER_CPP_PATH = "../giada/src/gui/langMapper.cpp"
DEST_LANGMAPS_PATH = "../giada-langmaps/langmaps"
DEST_ENGLISH_LANGMAP_PATH = f"{DEST_LANGMAPS_PATH}/english.langmap"


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


def get_source_langmap(h_file_path, cpp_file_path):
    """Turns the h/cpp file combo into a dict object. This is the source of truth
    of the langmap messages."""
    keys = get_langmapper_keys(h_file_path)
    values = get_langmapper_values(cpp_file_path, keys)
    langmap_dict = dict(values)
    return langmap_dict


def get_existing_langmap(file_path):
    """Reads an already existing JSON langmap file."""
    with open(file_path, "r") as f:
        return json.load(f)


def sync_langmap(file_path, source_langmap):
    """Updates all values in langmap at 'file_path' with content from 'source_langmap'.
    If 'file_path' points to the english langmap, the whole file is generated from
    scratch because that's the official reference. Otherwise, missing keys will
    be added in langmap file at 'file_path'."""
    if "english.langmap" in file_path:
        make_langmap(file_path, source_langmap)
        return
    target_langmap = get_existing_langmap(file_path)
    target_langmap_updated = target_langmap
    for key, value in source_langmap.items():
        if key not in target_langmap:
            print(f"'{key}' missing from '{pathlib.Path(file_path).name}', updating...")
            target_langmap_updated[key] = value
    make_langmap(file_path, target_langmap_updated)


def make_langmap(file_path, langmap_dict):
    with open(file_path, "w") as f:
        json.dump(langmap_dict, f, indent=4)


if __name__ == "__main__":
    """ Read the source langmap content from h/cpp files. """
    source_langmap = get_source_langmap(
        SOURCE_LANGMAPPER_H_PATH, SOURCE_LANGMAPPER_CPP_PATH
    )

    """ Sync all existing langmap files according to the source above. """
    for file in pathlib.Path(DEST_LANGMAPS_PATH).iterdir():
        if file.is_file() and file.suffix == ".langmap":
            print(f"Syncing {file.name}...")
            sync_langmap(file.as_posix(), source_langmap)
