import logging
import threading
import time
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
        self.server = WebsocketServer(self.conf["port"],
                                      host=self.conf["host"])
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

    def run(self):
        self.server.run_forever()

    def new_client(client, server):
        logging.info("WS: New Client")
        self.server.send_message_to_all("Hey all, a new client has joined us")

    def client_left(client, server):
        logging.info("WS: Client left")
        self.server.send_message_to_all("Hey all, a new client has joined us")

    def message_received(client, server, message):
        logging.info("WS: New message " + message)

    def disconnect(self):
        logging.info("WS:Disconnect")
        self.server.shutdown()


if __name__ == '__main__':
    ws = WsServer()
    ws.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt as e:
        ws.disconnect()
        raise e
