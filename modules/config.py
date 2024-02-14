# -*- coding: utf-8 -*-
import os
import json
from fastapi import APIRouter
from modules import crash_handler
from modules.paths import PATH_CONFIG, DIR_ROOT

APP_ID = -1
ACCESS_KEY = ''
ACCESS_KEY_SECRET = b''

APP_CONFIG = {}


def load_app_info():
    try:
        # Read the application information from config.
        path_app_info = os.path.join(DIR_ROOT, 'app_info.json')
        with open(path_app_info, 'r', encoding='utf-8') as app_info_file:
            app_info_config = json.load(app_info_file)
            # Read and replace the application info.
            global APP_ID, ACCESS_KEY, ACCESS_KEY_SECRET
            APP_ID = app_info_config['app-id']
            ACCESS_KEY = app_info_config['access-key']
            ACCESS_KEY_SECRET = app_info_config['access-key-secret'].encode()
    except Exception:
        crash_handler.show_crash_report()


def load():
    # Try to load the config from file.
    if os.path.isfile(PATH_CONFIG):
        with open(PATH_CONFIG, 'r') as config_file:
            global APP_CONFIG
            APP_CONFIG = json.load(config_file)
    # Some must have values needs to be set here.
    if 'record_size' not in APP_CONFIG or not isinstance(APP_CONFIG['record_size'], int):
        APP_CONFIG['record_size'] = 10


def save():
    with open(PATH_CONFIG, 'w') as config_file:
        json.dump(APP_CONFIG, config_file)
