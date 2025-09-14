import xml.etree.ElementTree as et
import argparse
import sys
import utils


SOURCE_PATH = "../giada/extras/com.giadamusic.Giada.metainfo.xml"
CHANGELOG_APP_PATH = "../giada/ChangeLog"
CHANGELOG_WEB_PATH = "../giada-www/src/data/changes.html"


def get_changes_from_xml(file_path, version):
    utils.check_file_existence(file_path)
    root = et.parse(file_path).getroot()
    version_el = root.find(f'.//release[@version="{version}"]')
    if version_el is None:
        print(f"Could not find release {version} in {file_path}!")
        sys.exit(1)
    description = version_el.find("description")
    if description is None:
        print(f"Could not find description for release {version} in {file_path}!")
        sys.exit(1)
    changes = description.findall(f"ul/li")
    if changes == []:
        print(f"Could not find list of changes for release {version} in {file_path}!")
        sys.exit(1)
    return [li.text.strip() for li in changes]


def update_app_changelog(file_path, version, date, changes):
    utils.check_file_existence(file_path)
    with open(file_path, "r") as f:
        content = f.read()
        if f"{version} ---" in content:
            print(
                f"App changelog already compiled for version {version}, nothing to do"
            )
            return
        changes_txt = f"{version} --- {date}\n"
        for change in changes:
            changes_txt += f"- {change}\n"
        changes_txt += "\n\n"
    with open(file_path, "w") as f:
        f.write(changes_txt + content)


def update_web_changelog(file_path, changes):
    utils.check_file_existence(file_path)
    with open(file_path, "w") as f:
        content = "<ul>\n"
        for change in changes:
            content += f"\t<li>{change}</li>\n"
        content += "</ul>"
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Changelog generator")

    parser.add_argument("--version", help="Version number, e.g. 1.0.0", required=True)

    parser.add_argument(
        "--date", help="Release date, e.g. January 5, 1990", required=True
    )

    args = vars(parser.parse_args())
    version = args["version"]
    date = args["date"]

    changes = get_changes_from_xml(SOURCE_PATH, version)

    update_app_changelog(CHANGELOG_APP_PATH, version, date, changes)
    update_web_changelog(CHANGELOG_WEB_PATH, changes)
