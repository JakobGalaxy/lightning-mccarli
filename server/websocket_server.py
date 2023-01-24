import asyncio
import websockets
from websockets import WebSocketServerProtocol
import json
import logging
from logging import Logger
from datetime import datetime
from config import websocket_server_config as config
import base64
import imageio
import io
import numpy as np
import cv2
from ball_detection import detect_ball


class ControlChannel:
    def __init__(self):
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)
        self.__subscribers: set = set()

    async def handle_message(self, websocket, message):
        message_type: str = message['type']

        if message_type == 'subscribe':
            self.__logger.debug(f'new client subscribed (count={len(self.__subscribers)})')
            self.__subscribers.add(websocket)
        elif message_type == 'publish':
            await self.__handle_publish_message(message)
        else:
            self.__logger.warning(f'unknown message type={message_type} for control-channel')

    async def __handle_publish_message(self, message):
        self.__logger.debug('received publish message')
        websockets.broadcast(self.__subscribers, json.dumps(message))


class VideoStreamChannel:
    def __init__(self):
        self.__logger: Logger = logging.getLogger(self.__class__.__name__)
        self.__subscribers: set = set()

    async def handle_message(self, websocket, message):
        message_type: str = message['type']

        if message_type == 'subscribe':
            self.__logger.debug(f'new client subscribed (count={len(self.__subscribers)})')
            self.__subscribers.add(websocket)
        elif message_type == 'publish_frame':
            await self.__handle_publish_frame_message(message)
        else:
            self.__logger.warning(f'unknown message type={message_type} for video_stream')

    async def __handle_publish_frame_message(self, message):
        self.__logger.debug('received publish-frame-message')

        # measure time difference
        timestamp: datetime = datetime.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        now: datetime = datetime.now()
        time_diff = now - timestamp

        self.__logger.debug(f'frame upload latency: {time_diff.total_seconds() * 1_000} ms')

        # decode image
        frame: str = message['frame']
        image: np.ndarray = imageio.v3.imread(io.BytesIO(base64.b64decode(frame)))
        image: np.ndarray = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # convert image from RGB to BGR

        # run ball detection
        # TODO: implement ball detection
        image: np.ndarray = detect_ball(image)

        # convert image to base64
        _, buffer = cv2.imencode('.png', image)
        base64_stream = base64.b64encode(buffer)

        # forward frame to all other subscribers
        self.__logger.debug(f'broadcasting frame to all subscribers (count={len(self.__subscribers)})')
        output_message: dict[str, any] = {
            'channel': 'video_stream',
            'type': 'frame_data',
            'frame': base64_stream.decode('utf-8')
        }
        websockets.broadcast(self.__subscribers, json.dumps(output_message))


class WebSocketServer:
    def __init__(self):
        self.__logger = logging.getLogger(self.__class__.__name__)
        self.__connections: set = set()
        self.__video_stream_channel: VideoStreamChannel = VideoStreamChannel()
        self.__control_channel: ControlChannel = ControlChannel()

    async def __handle_message(self, websocket):
        async for message in websocket:
            message = json.loads(message)
            channel: str = message['channel']

            self.__logger.debug(f'received message on channel={channel}')

            if channel == 'video_stream':
                await self.__video_stream_channel.handle_message(websocket, message)
            elif channel == 'control':
                await self.__control_channel.handle_message(websocket, message)
            else:
                self.__logger.warning(f'unknown channel={channel}')

    async def __handle_connection(self, websocket: WebSocketServerProtocol):
        self.__connections.add(websocket)

        self.__logger.info(f'new client connected')
        self.__logger.info(f'active connection count: {len(self.__connections)}')
        try:
            await self.__handle_message(websocket)
        finally:
            self.__connections.remove(websocket)

            self.__logger.info(f'client disconnected')
            self.__logger.info(f'active connection count: {len(self.__connections)}')

    async def run(self):
        async with websockets.serve(self.__handle_connection, config.HOST, config.PORT):
            self.__logger.info('server started successfully')
            await asyncio.Future()  # wait forever
