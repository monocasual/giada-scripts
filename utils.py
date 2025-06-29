import os
import sys


def check_file_existence(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} doesn't exist!")
        sys.exit(1)
