from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database


class LogicSelectCharacterCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["BrawlerID"] = stream.readDataReference()
        fields["BrawlerSlot"] = stream.readVInt()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        brawler_id = fields["BrawlerID"][1]
        if database.select_brawler(calling_instance.player.ID[1], brawler_id):
            calling_instance.player.reload()

    def getCommandType(self):
        return 525
