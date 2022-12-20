import asyncio
from websocket_server import WebSocketServer
import logging.config
import os

LOGGING_CONFIG_PATH: os.path = os.path.join(os.getcwd(), 'config', 'logging.conf')

if __name__ == "__main__":
    logging.config.fileConfig(LOGGING_CONFIG_PATH)
    server = WebSocketServer()
    asyncio.run(server.run())
