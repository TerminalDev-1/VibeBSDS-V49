from Classes.Commands.LogicCommand import LogicCommand
from Classes.Database import database
from Classes.Messaging import Messaging


class LogicClaimMasteryTrackRewardCommand(LogicCommand):
    def decode(self, stream):
        fields = {}
        LogicCommand.decode(stream, fields, False)
        fields["BrawlerID"] = stream.readDataReference()
        fields["RewardLevel"] = stream.readVInt()
        fields["Fallback"] = stream.readBoolean()
        LogicCommand.parseFields(fields)
        return fields

    def execute(self, calling_instance, fields, crypto_init=None):
        reference = fields["BrawlerID"]
        if reference is None or reference[0] != 16:
            return
        claimed, reason = database.claim_mastery(
            calling_instance.player.ID[1], reference[1], fields["RewardLevel"]
        )
        if claimed:
            calling_instance.player.reload()
            reward_id = {"Coins": 7, "PowerPoints": 24, "Credits": 22,
                         "ChromaCredits": 23, "UniqueEmote": 11,
                         "UniquePlayerIcon": 11, "UniqueTitle": 11}[reason["kind"]]
            Messaging.sendMessage(24111, {
                "Socket": calling_instance.client, "Command": {"ID": 203},
                "Boxes": [{"Type": 100, "Items": [{
                    "Amount": reason["amount"], "RewardID": reward_id,
                    "DataRef": reason["reference"] or [0, 0],
                }]}],
            }, crypto_init)
        else:
            print(f"Mastery claim rejected for {reference[1]}: {reason}")

    def getCommandType(self):
        return 569
