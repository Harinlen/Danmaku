# -*- coding: utf-8 -*-
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from modules import paths, config, danmaku, cache, skins, settings, crash_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load application information.
    config.load_app_info()
    # Load the configure file.
    config.load()
    # Restore the cache.
    cache.load_history_record()
    # Update the skin list.
    skins.update_installed_skins()
    # Start the danmaku fetching background work.
    if 'user_id' in config.APP_CONFIG and len(config.APP_CONFIG['user_id']) > 0:
        await danmaku.start_danmaku_fetcher(config.APP_CONFIG['user_id'])
    # Expand the event loop.
    yield
    # Stop the live room fetching tasks.
    danmaku.stop_danmaku_fetcher()


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
async def get_danmuki_instance():
    # Load the current skin homepage.
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
