# -*- coding: utf-8 -*-
import os
import winreg
from fontTools.ttLib import TTFont
from modules import paths

FONT_FAMILIES = []


def get_font_family_name(font_path: str) -> str:
    try:
        # Set the font.
        font = TTFont(font_path)
        family_name = ''
        for ii, i in enumerate(font['name'].names):
            if i.nameID == 1:
                # Check platform ID.
                if i.platformID == 3:
                    if i.langID == 2052:
                        return str(i.toUnicode())
                    family_name = str(i.toUnicode())
                    continue
                if i.platformID == 3:
                    if i.langID == 33:
                        return str(i.toUnicode())
                    family_name = str(i.toUnicode())
        return family_name
    except Exception:
        return ''


def load_custom_fonts():
    existed_fonts = set()
    # Construct the CSS file.
    with open(os.path.join(paths.DIR_STATICS, 'css', 'fonts.css'), 'w', encoding='utf-8') as css_file:
        # Construct the user font directory.
        path_user_font_dir = os.path.join(paths.DIR_STATICS, 'fonts')
        for filename in os.listdir(path_user_font_dir):
            suffix = filename[-4:].lower()
            if suffix != '.ttf' and suffix != '.otf':
                continue
            family_name = get_font_family_name(os.path.join(path_user_font_dir, filename))
            if family_name == '' and family_name not in existed_fonts:
                continue
            existed_fonts.add(family_name)
            # Construct the font CSS text.
            css_file.write('\n'.join([
                "@font-face {",
                '    font-family: "{}";'.format(family_name),
                '    src: url("/statics/fonts/{}");'.format(filename),
                "}",
                ""
            ]))
    return existed_fonts


def load_system_fonts():
    # Get the font directory.
    dir_font = os.path.join(os.path.abspath(os.getenv('SystemRoot')), 'Fonts')
    # Load all the font from registry.
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    fonts = winreg.OpenKey(reg,
                           r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts',
                           0, winreg.KEY_READ)
    def get_font_path(stored_path: str):
        if os.path.isfile(stored_path):
            return str(stored_path)
        else:
            font_path = os.path.join(dir_font, stored_path)
            if os.path.isfile(font_path):
                return font_path
        return None

    existed_fonts = set()
    with open(os.path.join(paths.DIR_STATICS, 'css', 'sys_fonts.css'), 'w', encoding='utf-8') as css_file:
        for i in range(0, winreg.QueryInfoKey(fonts)[1]):
            _, font_path, _ = winreg.EnumValue(fonts, i)
            font_path = get_font_path(font_path)
            if font_path is None:
                continue
            # Fetch the font family.
            family_name = get_font_family_name(font_path)
            if family_name == '' or family_name in existed_fonts:
                continue
            existed_fonts.add(family_name)
            css_file.write('\n'.join([
                "@font-face {",
                '    font-family: "{}";'.format(family_name),
                '    src: local("{}");'.format(family_name),
                "}",
                ""
            ]))
    return existed_fonts


def load_fonts():
    global FONT_FAMILIES
    # Load and update CSS font file.
    FONT_FAMILIES = list(load_custom_fonts()) + list(load_system_fonts())
    # Merge these two fonts.
    FONT_FAMILIES.sort()
