# -*- coding: utf-8 -*-
import os
import json
from modules import paths, config

SKIN_LIST = []


def get_skin_homepage(skin_name: str) -> str:
    return os.path.join(paths.DIR_SKINS, skin_name, 'index.html')


def get_current_skin() -> str:
    # When setting is available, return the saved value.
    if 'skin' in config.APP_CONFIG and len(config.APP_CONFIG['skin']) > 0:
        return config.APP_CONFIG['skin']
    # Or else, the first appear skin is the current.
    for skin_name in os.listdir(paths.DIR_SKINS):
        if os.path.isfile(get_skin_homepage(skin_name)):
            return skin_name
    return ''


def get_skin_info(skin_name: str) -> dict:
    skin_root = os.path.join(paths.DIR_SKINS, skin_name)
    if os.path.isdir(skin_root):
        # Check whether it has index.html.
        skin_entry = os.path.join(skin_root, 'index.html')
        if not os.path.isfile(skin_entry):
            return {}
        # Set the default skin info
        skin_states = {
            'name': skin_name,
            'url': skin_entry,
            'path': skin_root,
            'display': skin_name,
            'using': False
        }
        # Load the skin information.
        skin_info_path = os.path.join(skin_root, 'skin-info.json')
        if os.path.isfile(skin_info_path):
            try:
                with open(skin_info_path, 'r', encoding='utf-8') as skin_info_file:
                    skin_info = json.load(skin_info_file)
                    if 'name' in skin_info:
                        skin_states['display'] = skin_info['name']
            except Exception:
                pass
        return skin_states
    return {}


def update_installed_skins():
    global SKIN_LIST
    SKIN_LIST = []
    for dir_name in os.listdir(paths.DIR_SKINS):
        current_skin = get_skin_info(dir_name)
        if len(current_skin) == 0:
            continue
        SKIN_LIST.append(current_skin)


def load_skin_homepage(skin_name: str) -> str:
    # Construct the homepage file path.
    homepage_path = get_skin_homepage(skin_name)
    # Return the file content when file is existed.
    if os.path.isfile(homepage_path):
        with open(homepage_path, 'r', encoding='utf-8') as homepage_file:
            return homepage_file.read()
    # Construct a page when error happened.
    return '<html><body>无法加载弹幕机{}</body></html>'.format(skin_name)
