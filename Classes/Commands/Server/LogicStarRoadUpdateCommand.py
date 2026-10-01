from Classes.Commands.LogicCommand import LogicCommand
from Classes.Commands.LogicServerCommand import LogicServerCommand
from Classes.StarRoad import encode_star_road


class LogicStarRoadUpdateCommand(LogicServerCommand):
    def encode(self, fields):
        self.writeVInt(-1) # server command mutex; native base decoder 0x5caef8
        LogicCommand.encode(self, fields)
        encode_star_road(self, fields["OwnedBrawlers"], fields["Credits"])
        return self.messagePayload

    def getCommandType(self):
        return 227
