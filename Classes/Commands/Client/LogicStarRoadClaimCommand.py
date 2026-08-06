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
        brawler_id = fields["BrawlerID"][1]
        claimed, result = database.claim_star_road(
            calling_instance.player.ID[1], brawler_id
        )
        if claimed:
            calling_instance.player.reload()
            Messaging.sendMessage(
                24111,
                {
                    "Socket": calling_instance.client,
                    "Command": {"ID": 203},
                    "Boxes": [
                        {
                            "Type": 100,
                            "Items": [
                                {
                                    "Amount": 1,
                                    "DataRef": [16, brawler_id],
                                    "RewardID": 1,
                                }
                            ],
                        }
                    ],
                },
                crypto_init,
            )
        else:
            print(f"Star Road claim rejected for {brawler_id}: {result}")

    def getCommandType(self):
        return 562
