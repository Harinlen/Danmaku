# -*- coding: utf-8 -*-
import os
import webbrowser
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from server_settings import settings as serv_settings
from modules import paths, config, danmaku, cache, skins, settings, crash_handler, fonts


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load application information.
    if not config.load_app_info():
        crash_handler.show_error("错误", "找不到BiliBili项目配置文件，请创建app_info.json")
        return
    # Load the font from system.
    print('正在加载字体...')
    fonts.load_fonts()
    # Load the configure file.
    print('正在加载配置...')
    config.load()
    # Restore the cache.
    print('正在加载缓存...')
    cache.load_history_record()
    cache.load_emoji_cache()
    # Update the skin list.
    print('正在加载皮肤...')
    skins.update_installed_skins()
    # Start the danmaku fetching background work.
    print('正在登录...')
    if 'user_id' in config.APP_CONFIG and len(config.APP_CONFIG['user_id']) > 0:
        await danmaku.start_danmaku_fetcher(config.APP_CONFIG['user_id'])
    # Show the setting page.
    webbrowser.open("http://127.0.0.1:{}/settings/".format(serv_settings.PORT))
    # Expand the event loop.
    print('正在启动服务器...')
    yield
    # Stop the live room fetching tasks.
    danmaku.stop_danmaku_fetcher()
    # Flush the cache.
    print('正在保存缓存...')
    cache.flush_history_record()
    print('正在保存配置...')
    config.save()
    print('正在关闭系统...')


serv = FastAPI(lifespan=lifespan)
# Mapping cache and statics
serv.mount('/statics', StaticFiles(directory=os.path.join(paths.DIR_ROOT, 'statics')), name='statics')
# Directory ensure.
if not os.path.isdir(paths.DIR_CACHE):
    os.makedirs(paths.DIR_CACHE, exist_ok=True)
serv.mount('/cache', StaticFiles(directory=os.path.join(paths.DIR_ROOT, 'cache')), name='cache')
# Adding sub-routers.
serv.include_router(cache.router, prefix='/api')
serv.include_router(settings.router, prefix='/settings')
# Load the favicon.
with open(os.path.join(paths.DIR_ROOT, 'favicon.png'), 'rb') as favicon_file:
    favicon = favicon_file.read()


@serv.get('/', response_class=HTMLResponse)
async def get_danmuki_instance(skin_name: str = ''):
    # Load the current skin homepage.
    if len(skin_name) > 0:
        # Check whether skin exist.
        return skins.load_skin_homepage(skin_name)
    return skins.load_skin_homepage(skins.get_current_skin())


@serv.websocket('/danmaku')
async def live_danmaku_websocket(ws: WebSocket):
    # Register the websocket the client manager.
    await danmaku.manager.connect(ws)
    # All the client shouldn't send anything, so this is just a dead loop.
    while True:
        try:
            await ws.receive()
        except RuntimeError:
            danmaku.manager.disconnect(ws)
            break


@serv.get('/favicon.ico')
async def favicon():
    return FileResponse(path=os.path.join(paths.DIR_ROOT, 'favicon.png'))


@serv.exception_handler(Exception)
async def exception_handler(request, exc):
    crash_handler.show_crash_report()
