# VibeBSDS V49

**VibeBSDS V49** is a vibe-coded evolution of the BSDS V49.194 game server,
built and managed collaboratively by
[@TerminalDev-1](https://github.com/TerminalDev-1) and OpenAI Codex.

This README is also the project's living changelog. It records what was
actually built, what was verified on a real Android device, and what should not
be expected from the project.

VibeBSDS is not just BSDS with a new name. The base project could connect a
client and serve mostly hardcoded state. We pushed it substantially further:
accounts now survive restarts, battles change real stored progression, credits
can unlock brawlers, and HomeData is generated from the same database that
records the results. That is far beyond the original server's static demo
behavior.

## What we built beyond BSDS

- A versioned SQLite database created automatically as `player.sqlite`.
- Persistent account identity, login tokens, and Android-device recovery.
- Stored currencies, unlocked brawlers, selected brawler, power levels,
  trophies, mastery values, wins, losses, and battle history.
- Transactional battle rewards committed before the result packet is sent.
- Working total and per-brawler trophy progression.
- Working credit rewards and Star Road brawler unlocking.
- Database-backed character selection and profile/home values.
- Dynamic HomeData instead of the old hardcoded rank, trophy, and Power 11
  presentation.
- A playable Bounty event on Shooting Star, verified in a live device match
  with the correct star scoreboard and bounty indicators.
- Automated progression, database-integrity, and packet-encoding tests.
- A separately packaged Android client so the official Brawl Stars app is not
  overwritten.

Team victories currently award `+8` trophies, 20 Brawl Pass tokens, and 20
credits. Defeats award `-6` trophies, 10 tokens, and 8 credits, with a
five-trophy floor required for V49.194 client stability. Showdown-compatible
results retain a placement-based trophy table even though Showdown is not an
advertised live event today.

## What works right now

- V49.194 client login and reconnect
- Persistent accounts and progression
- Database-backed HomeData and profiles
- Trophy, token, and credit rewards
- Star Road credit spending and brawler unlocks
- Selected-brawler persistence
- Bounty on Shooting Star using the client's local/offline bot battle
- Battle history and reconnect persistence

The game server listens on TCP port `9339` by default. Device testing has been
performed with the included V49.194-compatible Android client.

## The honest limitation: do not expect Brawl Ball

**Brawl Ball is not on the roadmap and should not be expected to become
playable in this project.**

The V49 client can be made to display a Brawl Ball card, map, and scoreboard,
but it still instantiates Gem Grab behavior, including the gem mine and carried
gem counters. Alternative event slots activate the APK's unfinished,
never-ending "Selecting Event" roulette instead of a match. A Brawl Ball-looking
screen is therefore not the same thing as a working Brawl Ball battle, and this
project will not pretend otherwise.

Unless a substantially more capable future model—something in the spirit of a
hypothetical "GPT Astro"—or an unusually strong V49 protocol/client specialist
becomes available to the project, Brawl Ball should be treated as out of scope.
The stable game server deliberately advertises Bounty rather than shipping a
fake hybrid mode.

## Remaining work and known boundaries

- Battles use the client's local/offline bot simulation. This is not a
  server-authoritative real-time multiplayer battle engine.
- Brawl Ball is intentionally unsupported for the reasons above.
- Additional modes must be proven inside a live match before being advertised.
- Some surrounding club and social structures still originate from the base
  server and contain static placeholder data.
- The project is for development and learning, not production hosting,
  monetisation, official services, or official accounts.

## AI-generated-code disclosure

The new VibeBSDS implementation is openly **AI-generated and AI-assisted**.
OpenAI Codex produced most of the added code and documentation under
TerminalDev-1's direction, while TerminalDev-1 chose the product direction,
tested behavior, reported failures, and decided what was acceptable to ship.

That disclosure is not an excuse for unverified claims. Changes are tested with
automated checks and, where client behavior matters, on the actual Android
device. The failed Brawl Ball experiments are documented above precisely
because a convincing menu card is not proof of working gameplay.

## Download the Android client

Download the V49.194 APK from this repository's GitHub release:

- [Download `project-bsds-v49.apk`](https://github.com/TerminalDev-1/VibeBSDS-V49/releases/download/v49.194/project-bsds-v49.apk)
- SHA-256: `279A4E3F9D418E6639A10F5F22F25FECB848363D30D715067BE35DCC5BB5DEF9`
- Android package: `com.projectbsds.v49` (separate from the official game)

You can also download it with an authenticated GitHub CLI:

```powershell
gh release download v49.194 -R TerminalDev-1/VibeBSDS-V49 -p project-bsds-v49.apk
```

Before rebuilding the client, set `redirectHost` in
`lib/armeabi-v7a/libkagenay.c.so` to the game server computer's LAN IPv4
address. Keep `redirectPort` set to `9339`. The APK is distributed as a release
asset because a file this large should not be stored in normal Git history.

## Start the game server

Requirements:

- Python 3
- A V49.194-compatible client configured for the game server computer's LAN
  address and TCP port `9339`

Run:

```powershell
python Core.py
```

The game server binds to `0.0.0.0:9339`. Allow TCP port `9339` through the host
firewall when another device connects over the local network.

Run the test suite with:

```powershell
python -m unittest discover -s tests -v
```

## Project history

### Current VibeBSDS milestone

- Replaced ephemeral player objects with durable SQLite-backed accounts.
- Added real battle reward persistence and battle history.
- Added trophy, token, credit, Star Road, and brawler-selection logic.
- Rebuilt HomeData and profile data around stored player state.
- Added and device-verified playable Bounty.
- Investigated Brawl Ball deeply, rejected the misleading Gem Grab hybrid, and
  restored the client-proven Bounty configuration.
- Added regression tests for the progression and packet paths.

### BSDS foundation

This repository is derived from
[Zhany4ka/BSDS-V49](https://github.com/Zhany4ka/BSDS-V49), itself based on the
original BSDS work by [CrazorTheCat](https://github.com/CrazorTheCat). Their work
provided the V49 protocol foundation that made this expansion possible.

Additional upstream credits:

- [kagenay](https://github.com/kagenay) — Android client tooling
- [HaccerCat](https://github.com/HaccerCat) — crypto/client assistance
- [VitalikObject/OldBrawl](https://github.com/VitalikObject/OldBrawl) — crypto implementation

## Licence

Licensed under the [Apache License 2.0](LICENSE). Upstream attribution and
licence notices are retained.
