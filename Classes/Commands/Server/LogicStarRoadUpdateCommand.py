from Classes.Commands.LogicCommand import LogicCommand
from Classes.Commands.LogicServerCommand import LogicServerCommand


class LogicStarRoadUpdateCommand(LogicServerCommand):
    def encode(self, fields):
        self.writeVInt(1)
        self.writeString("")
        self.writeVInt(1)
        LogicCommand.encode(self, fields)
        return self.messagePayload

    def getCommandType(self):
        return 225
