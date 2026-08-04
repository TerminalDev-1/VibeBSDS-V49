from Classes.Messaging import Messaging
from Classes.Database import database

from Classes.Packets.PiranhaMessage import PiranhaMessage


class ChangeAvatarNameMessage(PiranhaMessage):
    def __init__(self, messageData):
        super().__init__(messageData)
        self.messageVersion = 0

    def encode(self, fields):
        self.writeString(fields["Name"])
        self.writeBoolean(fields["NameSetByUser"])

    def decode(self):
        fields = {}
        fields["Name"] = self.readString()
        fields["NameSetByUser"] = self.readBoolean()
        super().decode(fields)
        return fields

    def execute(message, calling_instance, fields, cryptoInit):
        database.update_name(calling_instance.player.ID[1], fields["Name"])
        calling_instance.player.reload()
        fields["Socket"] = calling_instance.client
        fields["Command"] = {"ID": 201}
        Messaging.sendMessage(24111, fields, cryptoInit)

    def getMessageType(self):
        return 10212

    def getMessageVersion(self):
        return self.messageVersion
