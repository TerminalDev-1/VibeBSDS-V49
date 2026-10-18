
# DisableNagle: reduce delay and improve performance between client and server BUT require more power #
# MinSecondsBetweenBattleResults: offline results are client-reported, so a result arriving sooner than
# this after the account's previous one is treated as a replay and not rewarded. 0 disables the check. #

settings = {
    "DisableNagle": True,
    "PrintEnabled": True,
    "MinSecondsBetweenBattleResults": 30,
}
