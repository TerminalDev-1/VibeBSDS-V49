import json

from Classes.Database import database


class Player:
    """Connection-local view of an account persisted by GameDatabase."""

    def __init__(self):
        self.ClientVersion = "0.0.0"
        self.ID = [0, 0]
        self.Token = ""
        self.Name = "Brawler"
        self.Registered = False
        self.Thumbnail = 0
        self.Namecolor = 0
        self.Region = "CA"
        self.ContentCreator = "VibeBSDS"
        self.Coins = 0
        self.Gems = 0
        self.StarPoints = 0
        self.ClubCoins = 0
        self.Credits = 0
        self.ChromaCredits = 0
        self.Fame = 0
        self.Trophies = 0
        self.HighestTrophies = 0
        self.TrophyRoadTier = 0
        self.Experience = 0
        self.Level = 1
        self.Tokens = 0
        self.TokensDoubler = 0
        self.SelectedBrawlers = [0]
        self.SelectedSkins = {}
        self.RandomizerSelectedSkins = []
        self.OwnedPins = [0, 1, 2, 3, 4]
        self.OwnedThumbnails = [0]
        self.OwnedBrawlers = {}
        self.BattleCount = 0
        self.WinCount = 0
        self.LoseCount = 0
        self.TutorialState = 2

    def load(self, account, brawlers):
        self.ID = [account["high_id"], account["low_id"]]
        self.Token = account["token"]
        self.Name = account["name"]
        self.Registered = bool(account["name_set"])
        self.Thumbnail = account["thumbnail"]
        self.Namecolor = account["name_color"]
        self.Region = account["region"]
        self.ContentCreator = account["creator"]
        self.Coins = account["coins"]
        self.Gems = account["gems"]
        self.StarPoints = account["star_points"]
        self.ClubCoins = account["club_coins"]
        self.Credits = account["credits"]
        self.ChromaCredits = account["chroma_credits"]
        self.Fame = account["fame"]
        self.Trophies = account["trophies"]
        self.HighestTrophies = account["highest_trophies"]
        self.Experience = account["experience"]
        self.Level = account["level"]
        self.Tokens = account["tokens"]
        self.TokensDoubler = account["token_doubler"]
        self.SelectedBrawlers = [account["selected_brawler"]]
        self.BattleCount = account["battle_count"]
        self.WinCount = account["wins"]
        self.LoseCount = account["losses"]
        self.TutorialState = account["tutorial_state"]
        self.OwnedBrawlers = {
            row["brawler_id"]: {
                "CardID": row["card_id"],
                "Skins": [],
                "Trophies": row["trophies"],
                "HighestTrophies": row["highest_trophies"],
                "PowerLevel": row["power_level"],
                "PowerPoints": row["power_points"],
                "State": row["state"],
                "MasteryPoints": row["mastery_points"],
                "MasteryClaimed": row["mastery_claimed"],
            }
            for row in brawlers
        }

    def reload(self):
        loaded = database.load(self.ID[1])
        if loaded:
            self.load(*loaded)

    def getDataTemplate(self, highid, lowid, token):
        loaded = database.login((highid, lowid), token)
        self.load(*loaded)
        return self.toJSON()

    def toJSON(self):
        return json.loads(json.dumps(self.__dict__, sort_keys=True, indent=4))
