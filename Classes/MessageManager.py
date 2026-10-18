import traceback
from Classes.Logic.LogicLaserMessageFactory import LogicLaserMessageFactory
from Classes.Messaging import Messaging


class MessageManager:
    def receiveMessage(self, messageType, messagePayload, cryptoInit):
        message = LogicLaserMessageFactory.createMessageByType(messageType, messagePayload)
        if message is None:
            return
        try:
            if message.isServerToClient():
                message.encode()
            else:
                message.fields = message.decode()
                message.execute(self, message.fields, cryptoInit)

        except Exception:
            print(traceback.format_exc())
            return
        # LobbyInfo follows each handled message, including keep-alives, which
        # is how the client's lobby text stays current. Skip it for unknown
        # messages and for handlers that failed.
        if messageType > 10100:
            Messaging.sendMessage(23457, {"Socket": self.client}, cryptoInit, self.player)
