import websockets
import cv2 as cv
import asyncio
capture = cv.VideoCapture(0)

async def post_image():
    async with websockets.connect('ws://localhost:8888/camera') as websocket:
        while True:
            ret, frame = capture.read()
            _, buffer = cv.imencode('.JPEG', frame)

            await websocket.send(buffer.tobytes())

if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        asyncio.run(post_image())
    except KeyboardInterrupt:
        pass


