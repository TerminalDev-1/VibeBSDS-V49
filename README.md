# VibeBSDS V49

**VibeBSDS V49** is a vibe-coded evolution of the BSDS V49.194 game server,
built and managed collaboratively by
[@TerminalDev-1](https://github.com/TerminalDev-1) and OpenAI Codex.

It is a public, self-hostable game server available on GitHub. Anyone can run
their own V49 instance with local accounts, persistent progression, and the
included compatible Android client.

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
- Working credits that persist into Star Road progression.
- Working Star Road spending and brawler unlocking.
- Partial Brawl Pass support: the pass and token progression are present, but
  reward claiming is not yet durably registered by the game server.
- Database-backed character selection and profile/home values.
- Dynamic HomeData instead of the old hardcoded rank, trophy, and Power 11
  presentation.
- A playable Bounty event on Shooting Star, verified in a live device match
  with the correct star scoreboard and bounty indicators.
- Gem Grab as the first advertised mode and Bounty as the second, both kept on
  the client-proven event path.
- Automated progression, database-integrity, and packet-encoding tests.
- A separately packaged Android client that can coexist with other installed
  clients.

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
- Credits saved into Star Road progression
- Star Road credit spending and brawler unlocks
- Brawl Pass display and token progression (reward claiming remains partial)
- Gem Grab as the first mode
- Bounty as the second mode
- Selected-brawler persistence
- Gem Grab and Bounty using the client's local/offline bot battles
- Battle history and reconnect persistence
- An early Battle End screen with partial result/progression support

The game server listens on TCP port `9339` by default. Device testing has been
performed with the included V49.194-compatible Android client.

## Brawl Ball: 0% now, perhaps 5% later

**With the models, protocol knowledge, and client behavior available to this
project today, there is no realistic path to playable Brawl Ball. Do not expect
it in the current version.**

The V49 client can be made to display a Brawl Ball card, map, and scoreboard,
but it still instantiates Gem Grab behavior, including the gem mine and carried
gem counters. Alternative event slots activate the APK's unfinished,
never-ending "Selecting Event" roulette instead of a match. A Brawl Ball-looking
screen is therefore not the same thing as a working Brawl Ball battle, and this
project will not pretend otherwise.

A future, substantially stronger model - something in the spirit of a
hypothetical "GPT Astro" - could justify trying again. Even then, our estimate
is only about a **5% chance** of making Brawl Ball genuinely playable, not a
promise that it will happen. The chance is not permanently zero, but it is
effectively zero with the current tools. Until that changes, the stable game
server deliberately advertises Bounty rather than shipping a fake hybrid mode.

## Remaining work and known boundaries

- Battles use the client's local/offline bot simulation. This is not a
  server-authoritative real-time multiplayer battle engine.
- Battle End is an early implementation. It can show a result and apply stored
  progression, but the complete presentation is not finished and the
  trophy-flying animation has not been implemented.
- Brawl Ball is unsupported today; a much stronger future model may trigger
  one more attempt, with an estimated 5% chance of success.
- Additional modes must be proven inside a live match before being advertised.
- Brawl Pass rewards need authoritative claim handling. When a credit reward is
  tapped, the game server must record that exact reward as claimed, transfer
  the exact credit amount into Star Road/the active brawler unlock target, and
  return the updated state to the client.
- The current Brawl Pass client can animate a credit transfer without the game
  server fully registering the claim, and the animation may appear to transfer
  only part of the reward. Claimed reward nodes also need to remain visibly and
  durably claimed so the client cannot offer the same reward repeatedly.
- Some surrounding club and social structures still originate from the base
  server and contain static placeholder data.
- VibeBSDS is intended to be downloaded and self-hosted. Each installation
  keeps its own accounts and progression in its local SQLite database.

## AI-generated-code disclosure

The inherited BSDS foundation is upstream code and is **not** being claimed as
AI-generated. However, **all new code that moved VibeBSDS beyond the base BSDS
server was generated by OpenAI Codex** under TerminalDev-1's direction. That
includes the database, persistent progression, trophy and credit logic, Star
Road integration, Bounty restoration, packet changes, and regression tests.
TerminalDev-1 chose the direction, tested the real client, reported failures,
and decided what was acceptable to ship.

That disclosure is not an excuse for unverified claims. Changes are tested with
automated checks and, where client behavior matters, on the actual Android
device. The failed Brawl Ball experiments are documented above precisely
because a convincing menu card is not proof of working gameplay.

## Download the Android client

Download the V49.194 APK from this repository's GitHub release:

- [Download `project-bsds-v49.apk`](https://github.com/TerminalDev-1/VibeBSDS-V49/releases/download/v49.194/project-bsds-v49.apk)
- SHA-256: `279A4E3F9D418E6639A10F5F22F25FECB848363D30D715067BE35DCC5BB5DEF9`
- Android package: `com.projectbsds.v49`

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
- Added partial Brawl Pass/token progression while documenting the unfinished
  authoritative reward-claim and claimed-state synchronization work.
- Rebuilt HomeData and profile data around stored player state.
- Added Gem Grab as the first mode and device-verified Bounty as the second.
- Added an early, partially working Battle End path; the trophy-flying
  animation remains future work.
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
