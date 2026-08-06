from Classes.Commands.LogicCommand import LogicCommand


class LogicStarRoadClaimBrawlerCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["Selection"] = stream.readVInt()
        LogicCommand.parseFields(fields)
        return fields

    def getCommandType(self):
        return 567
