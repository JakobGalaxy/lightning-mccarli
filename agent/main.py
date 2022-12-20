import asyncio
import websockets
import cv2
import base64
import json
from datetime import datetime

camera = cv2.VideoCapture(0)
scale_percent = 30


async def send_images(websocket):
    while True:
        _, frame = camera.read()
        dims = frame.shape
        width, height = int(dims[1] * scale_percent / 100), int(dims[0] * scale_percent / 100)
        new_dims = (width, height)
        downscaled_frame = cv2.resize(frame, new_dims, interpolation=cv2.INTER_AREA)
        _, buffer = cv2.imencode('.png', downscaled_frame)
        base64_stream = base64.b64encode(buffer)
        message = {
            'channel': 'video_stream',
            'type': 'publish_frame',
            'timestamp': str(datetime.now()),
            'frame': base64_stream.decode('utf-8'),
        }
        await websocket.send(json.dumps(message))
        await asyncio.sleep(0.01)


async def receive_commands(websocket):
    while True:
        response = await websocket.recv()
        print(response)


async def handler():
    async with websockets.connect('ws://localhost:5678') as websocket:
        await asyncio.gather(
            send_images(websocket),
            receive_commands(websocket)
        )

if __name__ == "__main__":
    asyncio.run(handler())
