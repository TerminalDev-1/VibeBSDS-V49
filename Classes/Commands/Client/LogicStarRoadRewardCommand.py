from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database
from Classes.Messaging import Messaging


class LogicStarRoadRewardCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["BrawlerID"] = stream.readDataReference()
        fields["PaymentResource"] = stream.readDataReference()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        reference = fields["BrawlerID"]
        if reference is None or reference[0] != 16 or fields["PaymentResource"] != [5, 19]:
            print("Star Road purchase rejected: unsupported brawler or payment resource")
            return
        brawler_id = reference[1]
        claimed, reason = database.claim_star_road(
            calling_instance.player.ID[1], brawler_id
        )
        if claimed:
            calling_instance.player.reload()
            player = calling_instance.player
            Messaging.sendMessage(24111, {
                "Socket": calling_instance.client, "Command": {"ID": 227},
                "OwnedBrawlers": list(player.OwnedBrawlers), "Credits": player.Credits,
            }, crypto_init)
        else:
            print(f"Star Road claim rejected for {brawler_id}: {reason}")

    def getCommandType(self):
        return 560
