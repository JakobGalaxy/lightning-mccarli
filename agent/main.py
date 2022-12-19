import asyncio
import websockets
import cv2
import base64

camera = cv2.VideoCapture(0)


async def send_image(websocket):
    _, frame = camera.read()
    _, buffer = cv2.imencode('.png', frame)
    base64_stream = base64.b64encode(buffer)
    await websocket.send("'channel': 'video_stream', 'type': 'publish', 'payload': " + str(base64_stream))


async def handler():
    async with websockets.connect('ws://localhost:4000') as websocket:
        while True:
            await send_image(websocket)
            response = await websocket.recv()
            print(response)
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(handler())
