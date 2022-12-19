import asyncio
import websockets
import cv2
import base64
import json
from datetime import datetime

camera = cv2.VideoCapture(0)


async def send_image(websocket):
    _, frame = camera.read()
    _, buffer = cv2.imencode('.png', frame)
    base64_stream = base64.b64encode(buffer)
    message = {
        'channel': 'video_stream',
        'type': 'publish_frame',
        'timestamp': str(datetime.now()),
        'frame': base64_stream.decode('utf-8'),
    }
    await websocket.send(json.dumps(message))


async def handler():
    async with websockets.connect('ws://localhost:5678/') as websocket:
        while True:
            await send_image(websocket)
            await asyncio.sleep(0.01)


if __name__ == "__main__":
    asyncio.run(handler())
