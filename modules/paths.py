# -*- coding: utf-8 -*-
import os

DIR_MODS = os.path.dirname(os.path.abspath(__file__))
DIR_ROOT = os.path.dirname(DIR_MODS)
DIR_CACHE = os.path.join(DIR_ROOT, 'cache')
DIR_STATICS = os.path.join(DIR_ROOT, 'statics')
DIR_SKINS = os.path.join(DIR_STATICS, 'skins')

PATH_DANMAKU_CACHE = os.path.join(DIR_CACHE, 'danmaku.json')
PATH_CONFIG = os.path.join(DIR_ROOT, 'config.json')
