# VibeBSDS V49

**VibeBSDS** is a vibe-coded evolution of the BSDS V49.194 game server.
It is built and managed collaboratively by
[@TerminalDev-1](https://github.com/TerminalDev-1) and OpenAI Codex.

The current server supports the Project BSDS V49 client and has been tested on
an Android device through the home/lobby login flow. It listens on TCP port
`9339` by default.

## Download the Android client

Download the V49.194 APK from this repository's GitHub release:

- [Download `project-bsds-v49.apk`](https://github.com/TerminalDev-1/VibeBSDS-V49/releases/download/v49.194/project-bsds-v49.apk)
- SHA-256: `279A4E3F9D418E6639A10F5F22F25FECB848363D30D715067BE35DCC5BB5DEF9`
- Android package: `com.projectbsds.v49` (separate from the official game)

You can also download it from a terminal authenticated with GitHub CLI:

```powershell
gh release download v49.194 -R TerminalDev-1/VibeBSDS-V49 -p project-bsds-v49.apk
```

Before rebuilding the client, set `redirectHost` in
`lib/armeabi-v7a/libkagenay.c.so` to the server computer's LAN IPv4 address.
Keep `redirectPort` set to `9339`. The APK is distributed as a release asset
because GitHub supports release files up to 2 GiB, while a file this large
should not be stored in normal Git history.

## Start the server

Requirements:

- Python 3
- A V49.194-compatible client configured to connect to the server computer's
  LAN address on port `9339`

Run:

```powershell
python Core.py
```

The server binds to `0.0.0.0:9339`. If another device is connecting over your
network, allow TCP port `9339` through the host firewall.

## Project status

This is a development and learning project. It is not intended for production
hosting, monetisation, interaction with official services, or use with an
official account.

Client APKs, signing keys, generated builds, logs, and local databases are not
stored in this repository.

## Credits

This repository is derived from
[Zhany4ka/BSDS-V49](https://github.com/Zhany4ka/BSDS-V49), itself based on the
original BSDS work by [CrazorTheCat](https://github.com/CrazorTheCat).

Additional upstream credits:

- [kagenay](https://github.com/kagenay) — Android client tooling
- [HaccerCat](https://github.com/HaccerCat) — crypto/client assistance
- [VitalikObject/OldBrawl](https://github.com/VitalikObject/OldBrawl) — crypto implementation

## Licence

Licensed under the [Apache License 2.0](LICENSE). Upstream attribution and
licence notices are retained.
