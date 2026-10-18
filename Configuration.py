
# DisableNagle: reduce delay and improve performance between client and server BUT require more power #
# MinSecondsBetweenBattleResults: offline results are client-reported, so a result arriving sooner than
# this after the account's previous one is treated as a replay and not rewarded. 0 disables the check. #

# Port: TCP port the game server listens on. It must match "redirectPort" in the client APK's
# lib/armeabi-v7a/libkagenay.c.so, so change both together. #

settings = {
    "Port": 9339,
    "DisableNagle": True,
    "PrintEnabled": True,
    "MinSecondsBetweenBattleResults": 30,
}

# Machine-specific overrides live in LocalConfiguration.py (gitignored), e.g.
# settings = {"Port": 9340} when the installed client redirects to 9340.
try:
    from LocalConfiguration import settings as _local_settings
except ImportError:
    _local_settings = {}
settings.update(_local_settings)
