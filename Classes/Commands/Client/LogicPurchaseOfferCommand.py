from Classes.Commands.LogicCommand import LogicCommand
from Classes.Messaging import Messaging


class LogicPurchaseOfferCommand(LogicCommand):
    def __init__(self, commandData):
        super().__init__(commandData)

    def encode(self, fields):
        LogicCommand.encode(self, fields)
        self.writeVInt(0)
        self.writeDataReference(0)
        return self.messagePayload

    def decode(self, calling_instance):
        fields = {}
        LogicCommand.decode(calling_instance, fields, False)
        fields["Unk1"] = calling_instance.readVInt()
        fields["Unk2"] = calling_instance.readDataReference()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        # Server-side offer purchases are unsupported. Ask the client to
        # resynchronise so its optimistic purchase is rolled back.
        if fields["Unk1"] == 0:
            Messaging.sendMessage(
                24104,
                {"Socket": calling_instance.client, "ServerChecksum": 0, "ClientChecksum": 0, "Tick": 0},
                crypto_init,
            )

    def getCommandType(self):
        return 519
