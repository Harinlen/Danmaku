# -*- coding: utf-8 -*-
import sys
import os
import shutil


def main():
    # Create the build directory.
    dir_root = os.path.dirname(os.path.abspath(__file__))
    dir_build = os.path.join(dir_root, 'build')

    if os.path.isdir(dir_build):
        shutil.rmtree(dir_build)
    if not os.path.isdir(dir_build):
        os.makedirs(dir_build, exist_ok=True)
    # Copy the file to build directory.
    dir_to_copy = ['runtime', 'statics', 'templates', 'py3k', 'modules']
    for dir_name in dir_to_copy:
        shutil.copytree(os.path.join(dir_root, dir_name), os.path.join(dir_build, dir_name))
    file_to_file = ['app_info.json', 'bootstrap.py', 'entry.py', 'launcher.exe', 'server.py', 'server_settings.py', 'favicon.png']
    for file_name in file_to_file:
        shutil.copyfile(os.path.join(dir_root, file_name), os.path.join(dir_build, file_name))
    return 0


if __name__ == '__main__':
    sys.exit(main())
