from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database
from Classes.Messaging import Messaging


class LogicClaimRankUpRewardCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["RewardTrack"] = stream.readVInt()
        fields["RewardType"] = stream.readVInt()
        fields["BrawlPassSeason"] = stream.readVInt()
        fields["Tier"] = stream.readVInt()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        claimed, result = database.claim_brawl_pass_credit(
            calling_instance.player.ID[1],
            fields["BrawlPassSeason"],
            fields["RewardTrack"],
            fields["Tier"],
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
                                {"Amount": result, "DataRef": [0, 0], "RewardID": 22}
                            ],
                        }
                    ],
                },
                crypto_init,
            )
        elif result != "not-credit":
            print(
                "Brawl Pass credit claim rejected for "
                f"season={fields['BrawlPassSeason']} "
                f"track={fields['RewardTrack']} tier={fields['Tier']}: {result}"
            )

    def getCommandType(self):
        return 517
