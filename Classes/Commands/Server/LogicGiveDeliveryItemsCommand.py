from Classes.Commands.LogicCommand import LogicCommand
from Classes.Commands.LogicServerCommand import LogicServerCommand


class LogicGiveDeliveryItemsCommand(LogicServerCommand):
    def decode(self, stream):
        return {}

    def encode(self, fields):
        self.writeVInt(0)
        boxes = fields["Boxes"]
        self.writeVInt(len(boxes))
        for box in boxes:
            self.writeVInt(box["Type"])
            self.writeVInt(len(box["Items"]))
            for item in box["Items"]:
                data_class, data_id = item["DataRef"]
                self.writeVInt(item["Amount"])
                self.writeDataReference(
                    data_class if data_class == 16 else 0,
                    data_id if data_class == 16 else 0,
                )
                self.writeVInt(item["RewardID"])
                for accepted_class in (29, (52, 28, 46), 23):
                    accepted = (
                        data_class in accepted_class
                        if isinstance(accepted_class, tuple)
                        else data_class == accepted_class
                    )
                    self.writeDataReference(
                        data_class if accepted else 0,
                        data_id if accepted else 0,
                    )
                self.writeVInt(0)
                self.writeVInt(0)

        # Native V49 decoder 0x5c8a2c: delivery context then server base.
        self.writeBoolean(False) # optional purchase receipt
        for key in ("Season", "RewardTrack", "Tier", "DeliveryIndex"):
            self.writeVInt(fields.get(key, 0))
        self.writeBoolean(False)
        self.writeBoolean(False)
        self.writeDataReference(*fields.get("RewardBrawler", [0, 0]))
        self.writeVInt(fields.get("MasteryLevel", -1))
        self.writeVInt(-1)
        self.writeVInt(-1) # mutex token before LogicCommand
        LogicCommand.encode(self, fields)
        return self.messagePayload

    def getCommandType(self):
        return 203
