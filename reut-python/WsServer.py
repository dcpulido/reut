import logging
import threading
from websocket_server import WebsocketServer

__author__ = "dcpulido91@gmail.com"


class WsServer(threading.Thread):
    def __init__(self,
                 conf=None,
                 controller=None):
        threading.Thread.__init__(self)
        if conf == None:
            self.conf = dict(port=4000,
                             host='127.0.0.1')
        else:
            self.conf = conf
        self.server = WebsocketServer(13254, host='127.0.0.1')
        self.server.set_fn_new_client(self.new_client)

    def run(self):
        self.server.run_forever()

    def new_client(client, server):
        self.server.send_message_to_all("Hey all, a new client has joined us")

    def disconnect(self):
        logging.info("WS:Disconnect")
        self.server.shutdown()


if __name__ == '__main__':
    ws = WsServer()
    ws.start()
    try:
        while True:
            pass
    except KeyboardInterrupt as e:
        ws.disconnect()
        raise e
