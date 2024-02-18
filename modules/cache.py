# -*- coding: utf-8 -*-
import base64
import os
import aiohttp
import json
import time
from urllib.parse import urlparse
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from modules import paths, config

EMPTY_PNG = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x03\x00\x00\x00%\xdbV\xca\x00\x00\x00\x03PLTE\x00\x00\x00\xa7z=\xda\x00\x00\x00\x01tRNS\x00@\xe6\xd8f\x00\x00\x00\nIDAT\x08\xd7c`\x00\x00\x00\x02\x00\x01\xe2!\xbc3\x00\x00\x00\x00IEND\xaeB`\x82'

DANMAKU_RECORD = []
DANMAKU_RECORD_LAST_MODIFIED = 0
DANMAKU_RECORD_LAST_SAVED = 0

IMAGE_CACHES = {}
EMOJI_CACHES = {}


def load_history_record():
    # Load the cache file from directory.
    if os.path.isfile(paths.PATH_DANMAKU_CACHE):
        with open(paths.PATH_DANMAKU_CACHE, 'r', encoding='utf-8') as danmu_history_file:
            global DANMAKU_RECORD
            DANMAKU_RECORD = json.load(danmu_history_file)


def push_history_record(record_info: str):
    global DANMAKU_RECORD, DANMAKU_RECORD_LAST_MODIFIED
    DANMAKU_RECORD.append(record_info)
    if len(DANMAKU_RECORD) > config.APP_CONFIG['record_size']:
        DANMAKU_RECORD.pop(0)
    DANMAKU_RECORD_LAST_MODIFIED = time.time()


def flush_history_record():
    global DANMAKU_RECORD_LAST_SAVED
    # Only save the record when it is changed.
    if DANMAKU_RECORD_LAST_MODIFIED != DANMAKU_RECORD_LAST_SAVED:
        with open(paths.PATH_DANMAKU_CACHE, 'w', encoding='utf-8') as danmu_history_file:
            json.dump(DANMAKU_RECORD, danmu_history_file)
        DANMAKU_RECORD_LAST_SAVED = DANMAKU_RECORD_LAST_MODIFIED


def clear_history_record():
    global DANMAKU_RECORD, DANMAKU_RECORD_LAST_MODIFIED
    DANMAKU_RECORD = []
    DANMAKU_RECORD_LAST_MODIFIED = time.time()
    flush_history_record()


def load_emoji_cache():
    global EMOJI_CACHES
    # Use the filename as the key of the image.
    for filename in os.listdir(paths.DIR_EMOJI):
        emoji_name, _ = os.path.splitext(filename)
        EMOJI_CACHES['[{}]'.format(emoji_name)] = '/statics/emoji/' + filename


router = APIRouter(prefix='/cache')


@router.get('/history_record', response_class=JSONResponse)
async def get_history_record():
    return [json.loads(x) for x in DANMAKU_RECORD]


@router.post('/history_record/flush')
async def save_history_record():
    # Only save the record when it is changed.
    flush_history_record()
    return {'status': 'success'}


@router.post('/image/{image_type}')
async def fetch_cache_image(request: Request, image_type: str):
    # Get the original URL.
    url_requested = await request.json()
    if 'url' not in url_requested:
        return {'url': ''}
    # Extract the file name from request URL.
    url = url_requested['url']
    local_filename = os.path.basename(urlparse(url).path)
    local_url = '/cache/{}/{}'.format(image_type, local_filename)
    # Check whether the image file is already existed.
    global IMAGE_CACHES
    if image_type not in IMAGE_CACHES:
        IMAGE_CACHES[image_type] = set()
    # Check whether the file is already in memory cache.
    if local_url in IMAGE_CACHES[image_type]:
        return {'url': local_url}
    # Check whether the file is already downloaded.
    local_key_dir = os.path.join(paths.DIR_CACHE, image_type)
    if not os.path.isdir(local_key_dir):
        os.makedirs(local_key_dir, exist_ok=True)
    local_filepath = os.path.join(local_key_dir, local_filename)
    if os.path.exists(local_filepath):
        # Add the file to memory cache.
        IMAGE_CACHES[image_type].add(local_filename)
        return {'url': local_url}
    # Download the file to the directory.
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return {'url': ''}
            # Try to read the response data.
            image_data = await response.read()
            # Write the filename to cache directory.
            with open(local_filepath, 'wb') as local_file:
                local_file.write(image_data)
            IMAGE_CACHES[image_type].add(local_filename)
            return {'url': local_url}


@router.get('/image_proxy')
async def fetch_single_image(url_encoded: str):
    try:
        url = base64.b64decode(url_encoded).decode('utf-8')
        # Extract the name from url.
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return Response(media_type='image/png', content=EMPTY_PNG)
                return Response(media_type='image/png', content=await response.read())
    except Exception:
        return Response(media_type='image/png', content=EMPTY_PNG)


@router.get('/emoji_map')
async def fetch_emoji_map():
    return EMOJI_CACHES
