import base64
from datetime import datetime

import tornado
import tornado.web
import tornado.websocket
import tornado.ioloop

import numpy as np
import cv2 as cv


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class ManipulatedHandler(tornado.websocket.WebSocketHandler):
    connection = None

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self, *args: str, **kwargs: str):
        print('new websocket manipulated from index.html')
        self.connection = self

    def on_close(self) -> None:
        print('deleted websocket manipulated from index.html')
        self.connection = None

# websocket connection from webpage / java script
class WebsocketHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def check_origin(self, origin: str) -> bool:
        return True

    def open(self, *args: str, **kwargs: str):
        print('new websocket from index.html')
        self.connections.add(self)

    def on_close(self) -> None:
        if self in self.connections:
            self.connections.remove(self)


# camera connections via websockets
# https://www.tornadoweb.org/en/stable/websocket.html
class CameraHandler(tornado.websocket.WebSocketHandler):
    connections = set()

    def open(self):

        if len(self.connections) > 3:
            self.close()
        else:
            print('new camera connection')
            self.connections.add(self)

    def on_close(self) -> None:
        if self in self.connections:
            self.connections.remove(self)

    def on_message(self, buffer):
        array_image = np.frombuffer(buffer, dtype=np.uint8)
        frame = cv.imdecode(array_image, cv.IMREAD_COLOR)
        if ManipulatedHandler.connection is not None:
            print("Send manipulated image")
            ManipulatedHandler.connection.write_message(base64.b64encode(frame))

        frame = self.add_time(frame)
        #frame = self.make_some_noise(frame)
        _, image = cv.imencode('.JPEG', frame)

        # send to all connected websockets via WebSocketHandler
        [client.write_message(base64.b64encode(image))
         for client in WebsocketHandler.connections]

    def add_time(self, frame):
        font = cv.FONT_HERSHEY_SIMPLEX
        position = (20, 20)
        font_scale = 1
        color = (255, 0, 0)
        thickness = 2

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        cv.putText(frame, current_time, position, font, font_scale, color, thickness, cv.LINE_AA)
        return frame

    def make_some_noise(self, frame):
        fgbg = cv.createBackgroundSubtractorMOG2()
        frame = fgbg.apply(frame)
        return frame


def make_app():
    return tornado.web.Application([
        (r'/', MainHandler),
        (r'/camera', CameraHandler),
        (r'/websocket', WebsocketHandler),
        (r'/websocketManipulated', ManipulatedHandler),
    ])


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()