from Classes.Logic.LogicCommandManager import LogicCommandManager
from Classes.Packets.PiranhaMessage import PiranhaMessage


class AvailableServerCommandMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        self.writeVInt(fields["Command"]["ID"])
        command = LogicCommandManager.createCommand(fields["Command"]["ID"], b"")
        # Encode from offset zero in a fresh stream. A prefixed buffer with a
        # zero offset makes packed booleans overwrite the command base.
        self.messagePayload += command.encode(fields)

    def decode(self):
        return {}

    def execute(message, calling_instance, fields):
        pass

    def getMessageType(self):
        return 24111

    def getMessageVersion(self):
        return self.messageVersion
