# -*- coding: utf-8 -*-
import os
import sys
import platform
import subprocess


def main():
    # Calculate the directory paths.
    dir_root = os.path.dirname(os.path.abspath(__file__))
    dir_py3k = os.path.join(dir_root, 'py3k')
    dir_runtime = os.path.join(dir_root, 'runtime')

    def start_webserver(python_path: str):
        # Start the server entry.
        try:
            subprocess.run([python_path, os.path.join(dir_root, 'entry.py')])
        except KeyboardInterrupt:
            return

    # Check whether the virtual environment is enabled.
    if sys.prefix != sys.base_prefix:
        # Directly start the website entry script.
        start_webserver(sys.executable)
        return 0
    # Update the virtual environment path.
    python_path = os.path.join(dir_py3k, "python.exe")
    # Construct the pyvenv.cfg
    venv_cfg = [
        "home = {}".format(dir_py3k),
        "include-system-site-packages = false",
        "version = {}".format(platform.python_version()),
        "executable = {}".format(python_path),
        "command = {} -m venv {}".format(python_path, dir_runtime)
    ]
    with open(os.path.join(dir_runtime, "pyvenv.cfg"), "w", encoding='utf-8') as venv_cfg_file:
        venv_cfg_file.write("\n".join(venv_cfg))
    # Run the script using virtual environment.
    start_webserver(os.path.join(dir_runtime, "Scripts", "python.exe"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
