# -*- coding: utf-8 -*-
import sys
import socket
import uvicorn
from server_settings import settings

DEBUG = False


def main():
    print("正在启动服务器...")

    def is_port_in_use(test_port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', test_port)) == 0

    for port in range(8170, 9000):
        if not is_port_in_use(port):
            settings.PORT = port
            print("弹幕机运行在 http://127.0.0.1:{}/".format(port))
            print("如要对弹幕机进行设置，请访问 http://127.0.0.1:{}/settings/".format(port))
            print("注意！在弹幕机运行过程中请不要关闭此窗口！")
            print("退出弹幕机请直接关闭本窗口和所有网页。")
            # Start the service at this port.
            uvicorn.run('server:serv',
                        port=port,
                        log_level='info' if DEBUG else 'critical',
                        )
            return 0


if __name__ == '__main__':
    sys.exit(main())
