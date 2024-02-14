# -*- coding: utf-8 -*-
import base64
import json
import os
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from modules import config, danmaku, templates, skins, paths

router = APIRouter()

SETTINGS_MENU_ITEM = [
    {
        'icon': 'house',
        'name': '直播间',
        'url': '/settings/'
    },
    {
        'icon': 'hdd',
        'name': '硬盘使用',
        'url': '/settings/storage'
    },
    {
        'icon': 'gear',
        'name': '弹幕机',
        'url': '/settings/danmaku'
    }
]


def select_menu_item(selected_id: int) -> list:
    item_info = SETTINGS_MENU_ITEM.copy()
    item_info[selected_id] = item_info[selected_id].copy()
    item_info[selected_id]['icon'] += '-fill'
    item_info[selected_id]['url'] = ''
    return item_info


def render_setting_page(request: Request, menu_items: list, panel_code: str,
                        selected_skin: str = ''):
    skin_items = [{'name': item['name'],
                   'display': item['display'],
                   'select': item['name'] == selected_skin}
                  for item in skins.SKIN_LIST]
    return templates.render(request, "settings.html",
                            {'setting_items': menu_items,
                                     'panel': panel_code,
                                     'skins': skin_items})


@router.get('/', response_class=HTMLResponse)
async def setting_home(request: Request):
    # Fetch user information from the user id.
    b_user_name = ''
    b_user_id = ''
    b_room_id = ''
    if len(config.APP_CONFIG['user_id']) > 0:
        verify_info = await danmaku.get_live_room_info(config.APP_CONFIG['user_id'])
        if verify_info['code'] == 0:
            user_info = verify_info['data']['anchor_info']
            b_user_name = user_info['uname']
            b_user_id = user_info['uid']
            b_room_id = user_info['room_id']
    # Render the room page.
    room_page = templates.render(
        request, 'settings_room.html',
        {'user_id_code': '未设置' if len(config.APP_CONFIG['user_id']) == 0 else config.APP_CONFIG['user_id'],
                 'user_name': b_user_name,
                 'room_id': b_room_id,
                 'user_id': b_user_id}).body.decode('utf-8')
    return render_setting_page(request, select_menu_item(0), room_page)


@router.get('/auth_bilibili', response_class=HTMLResponse)
async def get_bilibili_live_id(request: Request, close_url: str):
    # Transcode the close URL.
    close_url = base64.b64decode(close_url.encode()).decode()
    return templates.render(request, 'id_code_fetch.html', context={'close_url': close_url})


@router.post('/set_user_id')
async def set_user_id(request: Request):
    set_request_content = await request.json()
    if 'user_id' not in set_request_content:
        return {'status': 'failed', 'error': 'invalid request'}
    # Check user id is valid or not.
    candidate_user_id = set_request_content['user_id']
    # Verify the user id.
    verify_info = await danmaku.get_live_room_info(candidate_user_id)
    if 'code' not in verify_info or verify_info['code'] != 0:
        return {'status': 'failed'}
    # Replace the current user id.
    config.APP_CONFIG['user_id'] = candidate_user_id
    # If we have to save the user id, save it to config.
    if 'save' in set_request_content and isinstance(set_request_content['save'], bool) and set_request_content['save']:
        config.APP_CONFIG['user_id'] = set_request_content['user_id']
        config.save()
    # Restart the danmaku fetcher.
    await danmaku.start_danmaku_fetcher(config.APP_CONFIG['user_id'])
    return {'status': 'success', 'user_id': config.APP_CONFIG['user_id']}


@router.get('/storage')
async def setting_storage(request: Request):
    storage_page = templates.render(request, "settings_storage.html")
    return render_setting_page(request, select_menu_item(1),
                               storage_page.body.decode('utf-8'))


@router.get('/show-in-explorer/{path}')
async def show_directory(path: str):
    expect_dir_path = os.path.join(paths.DIR_ROOT, *path.split('-'))
    if os.path.isdir(expect_dir_path):
        # Show the directory in explorer.
        os.startfile(expect_dir_path)
    return {'status': 'success'}


@router.get('/danmaku')
async def setting_danmaku(request: Request):
    # Find the name of the installed skin.
    current_skin = skins.get_current_skin()
    current_skin_name = ''
    # Get teh current skin list.
    skin_list = skins.SKIN_LIST.copy()
    for ii, skin in enumerate(skins.SKIN_LIST):
        if skin['name'] == current_skin:
            skin_list[ii] = skin_list[ii].copy()
            skin_list[ii]['using'] = True
            current_skin_name = skin_list[ii]['display']
            break

    # Render the page.
    danmaku_page = templates.render(request, 'settings_danmaku.html', {
        'current_skin_name': current_skin_name,
        'installed_skins': skin_list
    }).body.decode('utf-8')
    return render_setting_page(request, select_menu_item(2), danmaku_page)


CLIENT_REFRESH_PACKET = json.dumps({'cmd': 'MTC_REFRESH'})


@router.get('/set-skin')
async def setting_set_skin(name: str):
    try:
        config.APP_CONFIG['skin'] = name
        config.save()
        # Ask all the client to refresh.
        await danmaku.manager.broadcast(CLIENT_REFRESH_PACKET)
        return {'status': 'success'}
    except Exception:
        return {'status': 'failed'}


@router.get("/skin-config/{skin_name}")
async def setting_skin_tweak(request: Request, skin_name: str):
    # Load the skin info.
    skin_info = skins.get_skin_info(skin_name)
    # Check whether there is any setting page existed.
    setting_path = os.path.join(skin_info['path'], 'settings.html')
    if os.path.isfile(setting_path):
        with open(setting_path, 'r', encoding='utf-8') as setting_file:
            config_code = setting_file.read().encode('utf-8')
    else:
        config_code = templates.render(request, 'settings_skin_empty.html').body.decode('utf-8')
    # Render the skin setting page.
    skin_setting_page = templates.render(request, "settings_skin.html", {
            'skin_name': skin_name,
            'skin_display': skin_info['display'],
            'using': skin_name == skins.get_current_skin(),
            'config_code': config_code
        })
    return render_setting_page(request, SETTINGS_MENU_ITEM, skin_setting_page.body.decode('utf-8'), skin_name)
