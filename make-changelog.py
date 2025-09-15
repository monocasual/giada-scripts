import xml.etree.ElementTree as et
import argparse
import sys
import utils
import datetime


SOURCE_PATH = "../giada/extras/com.giadamusic.Giada.metainfo.xml"
CHANGELOG_APP_PATH = "../giada/ChangeLog"
CHANGELOG_WEB_PATH = "../giada-www/src/data/changes.html"


class Changes:
    def __init__(self, version, codename, date, changes_list, description):
        self.version = version
        self.codename = codename
        self.date = date
        self.changes_list = changes_list
        self.description = description


def get_xml_element_content(el):
    return "".join(et.tostring(e, encoding="unicode") for e in el)


def get_changes_from_xml(file_path, version, codename):
    utils.check_file_existence(file_path)
    root = et.parse(file_path).getroot()
    version_el = root.find(f'.//release[@version="{version}"]')
    if version_el is None:
        print(f"Could not find release {version} in {file_path}!")
        sys.exit(1)
    date = datetime.datetime.strptime(version_el.get("date"), "%Y-%m-%d").date()
    description = version_el.find("description")
    if description is None:
        print(f"Could not find description for release {version} in {file_path}!")
        sys.exit(1)
    changes = description.findall(f"ul/li")
    if changes == []:
        print(f"Could not find list of changes for release {version} in {file_path}!")
        sys.exit(1)
    changes_list = [li.text.strip() for li in changes]
    return Changes(
        version, codename, date, changes_list, get_xml_element_content(description)
    )


def update_app_changelog(file_path, changes):
    utils.check_file_existence(file_path)
    with open(file_path, "r") as f:
        content = f.read()
        if f"{changes.version} ---" in content:
            print(
                f"App changelog already compiled for version {changes.version}, nothing to do"
            )
            return
        changes_txt = f"{changes.version} --- {changes.date.strftime("%Y . %m . %d")}\n"
        for change in changes.changes_list:
            changes_txt += (
                f"- {change.rstrip(";.")}\n"  # Remove . and ; characters at the end
            )
        changes_txt += "\n\n"
    with open(file_path, "w") as f:
        f.write(changes_txt + content)


def update_web_changelog(file_path, changes):
    utils.check_file_existence(file_path)
    with open(file_path, "w") as f:
        f.write(changes.description)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Changelog generator")

    parser.add_argument("--version", help="Version number, e.g. 1.0.0", required=True)
    parser.add_argument("--codename", help="Codename, e.g. Jackalope", required=True)

    args = vars(parser.parse_args())
    version = args["version"]
    codename = args["codename"]

    changes = get_changes_from_xml(SOURCE_PATH, version, codename)

    update_app_changelog(CHANGELOG_APP_PATH, changes)
    update_web_changelog(CHANGELOG_WEB_PATH, changes)
