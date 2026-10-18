import time
import socket
import threading
import traceback

from Classes.ClientsManager import ClientsManager
from Classes.Instances.Classes.Player import Player
from Classes.MessageManager import MessageManager
from Classes.Messaging import Messaging
from Classes.Crypto import Crypto


class Connection(threading.Thread):
    # A client that sends nothing for this long is treated as disconnected.
    # The client keeps sending keep-alives during offline matches; the limit is
    # generous because the old 7-second check never actually fired.
    IDLE_TIMEOUT = 60

    def __init__(self, socket, address):
        super().__init__()
        self.client = socket
        self.address = address
        self.player = Player()
        self.timeout = time.time()

    def recv(self, n):
        data = bytearray()
        while len(data) < n:
            packet = self.client.recv(n - len(data))
            if not packet:
                return b''
            data.extend(packet)
        return data

    def disconnect(self):
        print(f"Client with ip: {self.address} disconnected!")
        allSockets = ClientsManager.GetAll()
        if self.player.ID[1] in allSockets.keys() and allSockets[self.player.ID[1]]["Socket"] == self.client:
            ClientsManager.RemovePlayer(self.player.ID)
        self.client.close()

    def run(self):
        cryptoInit = Crypto()
        # Without a socket timeout a silent client blocks recv forever and the
        # idle check never runs.
        self.client.settimeout(Connection.IDLE_TIMEOUT)
        try:
            while True:
                # Read the full 7-byte header; a short read would otherwise
                # desynchronise every later message on this connection.
                messageHeader = self.recv(7)
                if len(messageHeader) < 7:
                    break
                headerData = Messaging.readHeader(messageHeader)
                self.timeout = time.time()
                packetPayload = self.recv(headerData[1])
                if len(packetPayload) < headerData[1]:
                    break
                packetID = headerData[0]
                packetPayload = cryptoInit.decryptClient(packetID, bytes(packetPayload))
                if packetPayload is None:
                    print(f"Client with ip: {self.address} sent a packet that failed authentication")
                    break
                # print("Received", packetID, LogicLaserMessageFactory.getMessageName(packetID), "length", headerData[1], "data", packetPayload, '\n')
                MessageManager.receiveMessage(self, packetID, packetPayload, cryptoInit)

        except (ConnectionError, socket.timeout):
            pass

        except Exception:
            print(traceback.format_exc())

        self.disconnect()
