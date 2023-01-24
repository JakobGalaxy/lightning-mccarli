import tornado.ioloop
import tornado.websocket

class MovementClient:
    def __init__(self, io_loop):
        self.connection = None
        self.io_loop = io_loop
        
    def start(self):
        self.connect()
        
    def connect(self):
        print('Try to connect ...')
        tornado.websocket.websocket_connect(
            url=f'ws://localhost:8888/movement',
            callback = self.retry_connection,
            on_message_callback = self.on_message,
            ping_interval = 10,
            ping_timeout = 30,
        )
        
    def retry_connection(self, future):
        try:
            self.connection = future.result()
            print('Connected')
        except:
            print('Reconnect failed')
            self.io_loop.call_later(3, self.connect)
        pass
        
    def on_message(self, message):
        print(f'{message}')
        #do the GPIO magic
        pass

def runTheClient():
    # event loop from tornado
    io_loop = tornado.ioloop.IOLoop.current()
    
    
    client = MovementClient(io_loop)
    io_loop.add_callback(client.start)
    
    io_loop.start()
    

if __name__ == '__main__':
    runTheClient()
