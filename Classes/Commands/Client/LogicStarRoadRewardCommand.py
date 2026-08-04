from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database
from Classes.Messaging import Messaging


class LogicStarRoadRewardCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["BrawlerID"] = stream.readDataReference()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        brawler_id = fields["BrawlerID"][1]
        claimed, reason = database.claim_star_road(
            calling_instance.player.ID[1], brawler_id
        )
        if claimed:
            calling_instance.player.reload()
            # A fresh HomeData is authoritative and makes the next credits target
            # immediately clickable without relying on client-only state.
            Messaging.sendMessage(
                24101,
                {"Socket": calling_instance.client},
                crypto_init,
                calling_instance.player,
            )
        else:
            print(f"Star Road claim rejected for {brawler_id}: {reason}")

    def getCommandType(self):
        return 560
