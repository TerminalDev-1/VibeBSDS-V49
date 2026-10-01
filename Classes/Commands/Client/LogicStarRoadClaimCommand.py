from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database
from Classes.Messaging import Messaging


class LogicStarRoadClaimCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["BrawlerID"] = stream.readDataReference()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        reference = fields["BrawlerID"]
        if reference is None or reference[0] != 16:
            return
        player = calling_instance.player
        claimed, reason = database.claim_star_road(player.ID[1], reference[1])
        if not claimed:
            print(f"Star Road claim rejected for {reference[1]}: {reason}")
            return
        player.reload()
        Messaging.sendMessage(24111, {
            "Socket": calling_instance.client, "Command": {"ID": 203},
            "RewardBrawler": reference,
            "Boxes": [{"Type": 25, "Items": [{
                "Amount": 1, "DataRef": reference, "RewardID": 1,
            }]}],
        }, crypto_init)
        Messaging.sendMessage(24111, {
            "Socket": calling_instance.client, "Command": {"ID": 227},
            "OwnedBrawlers": list(player.OwnedBrawlers), "Credits": player.Credits,
        }, crypto_init)

    def getCommandType(self):
        return 562
