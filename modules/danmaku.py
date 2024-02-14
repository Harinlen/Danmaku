# -*- coding: utf-8 -*-
import asyncio
import aiohttp
import time
import hashlib
import random
import struct
import websockets
import hmac
from modules import config, cache
from fastapi import WebSocket

BILIBILI_HOST = 'https://live-open.biliapi.com'
DANMAKU_FETCHER = None
DANMAKU_HEARTBEAT = None


def request_header(message: bytes) -> dict:
    # Extract the timestamp.
    ts = time.time()
    # Extract the MD5 digest of the message.
    md5 = hashlib.md5()
    md5.update(message)
    # Construct the header map.
    header_map = {
        "x-bili-timestamp": str(int(ts)),
        "x-bili-signature-method": "HMAC-SHA256",
        "x-bili-signature-nonce": str(random.randint(1, 100000)+ts),
        "x-bili-accesskeyid": config.ACCESS_KEY,
        "x-bili-signature-version": "1.0",
        "x-bili-content-md5": md5.hexdigest(),
    }
    header_list = sorted(header_map)
    header_str = '\n'.join((key + ":" + str(header_map[key])) for key in header_list)
    signature = hmac.new(config.ACCESS_KEY_SECRET, header_str.encode(), digestmod=hashlib.sha256).hexdigest()
    header_map["Authorization"] = signature
    header_map["Content-Type"] = "application/json"
    header_map["Accept"] = "application/json"
    return header_map


def proto_pack(body: bytes, op) -> bytes:
    packet_len = len(body) + 16
    return (struct.pack('>i', packet_len) +
            struct.pack('>h', 16) +
            struct.pack('>h', 0) +
            struct.pack('>i', op) +
            struct.pack('>i', 0) +
            body)


def proto_unpack(buf: bytes):
    if len(buf) < 16:
        return None
    packet_len = struct.unpack('>i', buf[0:4])[0]
    header_len = struct.unpack('>h', buf[4:6])[0]
    ver = struct.unpack('>h', buf[6:8])[0]
    op = struct.unpack('>i', buf[8:12])[0]
    seq = struct.unpack('>i', buf[12:16])[0]

    body = buf[16:packet_len]
    if ver == 0:
        return op, body
    else:
        return None


async def get_live_room_info(id_code: str):
    params = '{"code":"%s","app_id":%d}' % (id_code, config.APP_ID)
    async with aiohttp.ClientSession() as session:
        async with session.post("%s/v2/app/start" % BILIBILI_HOST,
                                data=params.encode(),
                                headers=request_header(
                                    params.encode())) as response:
            pack_info = await response.json()
        if pack_info['code'] != 0:
            return {'code': pack_info['code'],
                    'message': pack_info['message']}
        # Extract the game id to close the request.
        game_id = str(pack_info['data']['game_info']['game_id'])
        params = '{"game_id":"%s","app_id":%d}' % (game_id, config.APP_ID)
        # Close the app directly, just follow the official demo.
        async with session.post("%s/v2/app/end" % BILIBILI_HOST,
                                data=params.encode(),
                                headers=request_header(
                                    params.encode())) as response:
            await response.json()
    return pack_info


async def danmaku_heartbeat(ws):
    # Construct the heartbeat packet.
    heartbeat_packet = proto_pack(b'', 2)
    # Send the packet for every 20 seconds.
    while True:
        try:
            await asyncio.ensure_future(asyncio.sleep(20))
            await ws.send(heartbeat_packet)
        except KeyboardInterrupt:
            break


class ClientManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str) -> None:
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ClientManager()


async def danmaku_fetcher(ws):
    # Keep fetching the danmaku packet from live room.
    while True:
        try:
            op, recv_buf = proto_unpack(await ws.recv())
            if op == 3:
                continue
            # Parse the pack data.
            danmaku_pack = recv_buf.decode('utf-8')
            # Save into history record.
            cache.push_history_record(danmaku_pack)
            # Boardcast the current info to all the websocket.
            await manager.broadcast(danmaku_pack)
        except KeyboardInterrupt:
            break


async def start_danmaku_fetcher(user_id: str):
    # Stop the previous danmaku fetcher.
    stop_danmaku_fetcher()
    # Fetch the live room information.
    live_room_info = await get_live_room_info(user_id)
    if live_room_info['code'] != 0:
        # Cannot fetch any information, quit.
        print('无效的直播身份码 ({})，请重新设置。'.format(user_id))
        return
    # Extract the information from the pack info.
    wss_urls = live_room_info['data']['websocket_info']['wss_link']
    auth_body = str(live_room_info['data']['websocket_info']['auth_body']).encode()
    # Start the live room WebSocket.
    ws = await websockets.connect(wss_urls[0])
    # Send the authentication information.
    await ws.send(proto_pack(auth_body, 7))
    # Get the reply info of the auth body.
    await ws.recv()
    # Start the fetcher task and heartbeat task.
    print('身份码 {} 成功连接到直播间...'.format(user_id))
    global DANMAKU_FETCHER, DANMAKU_HEARTBEAT
    DANMAKU_FETCHER = asyncio.ensure_future(danmaku_fetcher(ws))
    DANMAKU_HEARTBEAT = asyncio.ensure_future(danmaku_heartbeat(ws))


def stop_danmaku_fetcher():
    global DANMAKU_FETCHER, DANMAKU_HEARTBEAT
    # Cancel the asyncio tasks execution.
    if not isinstance(DANMAKU_FETCHER, asyncio.Task):
        return
    print('正在关闭弹幕机...')
    if isinstance(DANMAKU_FETCHER, asyncio.Task):
        DANMAKU_FETCHER.cancel()
        DANMAKU_FETCHER = None
    if isinstance(DANMAKU_HEARTBEAT, asyncio.Task):
        DANMAKU_HEARTBEAT.cancel()
        DANMAKU_HEARTBEAT = None
