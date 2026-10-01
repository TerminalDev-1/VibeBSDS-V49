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

For the full evidence-backed feature record, see
[`improvements.md`](improvements.md). For the less diplomatic comparison, see
[`roast.md`](roast.md).

VibeBSDS is not just BSDS with a new name. The base project could connect a
client and serve mostly hardcoded state: Brawl Pass appeared, Star Road did
not appear at all, every brawler was unlocked, and players received the same
Rank 1/1,250-trophy presentation. We pushed it substantially further:
accounts now survive restarts, battles change real stored progression, credits
can unlock brawlers, and HomeData is generated from the same database that
records the results. That is far beyond the original server's static demo
behavior.

Every verified improvement and substantial investigation is documented in both
this README and improvements.md before its checkpoint is committed and pushed.
The record distinguishes live-device evidence, automated checks, and remaining
limitations while retaining credit for the upstream BSDS foundation.

## What we built beyond BSDS

- A versioned SQLite database created automatically as `player.sqlite`.
- Persistent account identity, login tokens, and Android-device recovery.
- Stored currencies, unlocked brawlers, selected brawler, power levels,
  trophies, mastery values, wins, losses, and battle history.
- Transactional battle rewards committed before the result packet is sent.
- Working total and per-brawler trophy progression.
- Complete credit flow for battles and known V49 Brawl Pass credit nodes:
  exact rewards persist into Star Road, survive reconnects, and cannot be
  claimed twice.
- Durable Star Road spending and brawler unlocking, with the next target
  updating in the same session and the reward reveal dismissing without reconnect.
- Partial Brawl Pass support: display, tokens, and credit rewards work; other
  pass reward types remain incomplete.
- Database-backed character selection and profile/home values.
- Dynamic HomeData instead of the old hardcoded rank, trophy, and Power 11
  presentation.
- A playable Bounty event on Shooting Star, verified in a live device match
  with the correct star scoreboard and bounty indicators.
- Gem Grab as the first advertised mode and Bounty as the second, both kept on
  the client-proven event path.
- Native offline-bot roster and special-skill guards that fix Gem Grab Play
  crashes, plus Bounty score enforcement that ends the match at 20.
- Correct V49 Battle End packets with player-relative outcomes, result teams,
  database battle receipts, and pre-battle score/high-score snapshots for reward animation.
- Automated progression, database-integrity, and packet-encoding tests.
- A separately packaged Android client that can coexist with other installed
  clients.

Team victories currently award `+750` trophies, 20 Brawl Pass tokens, and 20
credits. Defeats award `0` trophy change, 10 tokens, and 8 credits, with a
five-trophy floor required for V49.194 client stability. Showdown-compatible
results retain a placement-based trophy table even though Showdown is not an
advertised live event today.


The October 1 trophy-policy update changes team wins from +8 to +750 trophies
and defeats from -6 to zero trophy loss. Tokens and credits retain their
existing amounts; draws and the unadvertised Showdown placement table are
unchanged. A live Bounty win displayed Victory +750, raised account trophies
from 60 to 810 and Shelly from 55 to 805, and retained both values after
reconnect. Zero-loss defeats on either team are covered by regression tests,
not a separate live defeat. This server change works with the published APK.

## What works right now

- V49.194 client login and reconnect
- Persistent accounts and progression
- Database-backed HomeData and profiles
- Trophy, token, and credit rewards
- Credits saved into Star Road progression
- Star Road credit spending and brawler unlocks
- Brawl Pass display, token progression, and persistent credit rewards
- Gem Grab as the first mode
- Bounty as the second mode
- Selected-brawler persistence
- Gem Grab and Bounty using the client's local/offline bot battles
- Battle history and reconnect persistence
- Shared Battle End result and reward screens for Gem Grab and Bounty
- Correct player-relative victory/defeat and result-screen team placement
- Trophy-bar and token-counter animation with durable rewards

The 2026-10-01 development client was tested on the Xiaomi Pad 6: Gem Grab
Play reached Hard Rock Mine and completed the result/reward flow; Bounty
reached exactly `20/20` with `1:19` left and entered the victory screen.
Those earlier checks used the previous `+8` trophy reward, 20 tokens, and 20 credits. Gem Grab trophies
survived app/server restarts, and the final Bounty reward matched the database.
Defeat/draw outcomes and either-team conversion are covered by regression
tests; those outcomes were not separately proven in live matches.

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
- Battle End now reaches the result screen, reward screen, and Home. Trophy
  bars and token counters animate. Individual flying trophy sprites remain
  unfinished. The offline client does not report kills, damage, healing, or
  MVP data, so those statistics remain empty.
- Brawl Ball is unsupported today; a much stronger future model may trigger
  one more attempt, with an estimated 5% chance of success.
- Additional modes must be proven inside a live match before being advertised.
- Non-credit Brawl Pass rewards still need their own authoritative handlers.
  Credit nodes are handled separately and are complete for the known V49
  seasons encoded by the game server.
- Star Road credit unlocks now advance in the same session and the reward
  reveal can be dismissed. Gem purchases are not implemented server-side.
- Some surrounding club and social structures still originate from the base
  server and contain static placeholder data.
- Some brawler-specific behavior/content remains unfinished.
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

Codex also drove the fast code-test-device loop through wireless Android
debugging on the Xiaomi Pad 6: changing packets, restarting the game server,
entering matches, capturing evidence, and checking reconnect persistence.

That disclosure is not an excuse for unverified claims. Changes are tested with
automated checks and, where client behavior matters, on the actual Android
device. The failed Brawl Ball experiments are documented above precisely
because a convincing menu card is not proof of working gameplay.

## Download the Android client

Download the V49.194 APK from this repository's GitHub release:

- [Download `VibeBSDS-V49.apk`](https://github.com/TerminalDev-1/VibeBSDS-V49/releases/download/v49.194/VibeBSDS-V49.apk)
- SHA-256: `1B22AB6C97A8ED894AF5F9918FED4C5FD93AF4BAB83203B97097921F8EAA28BB`
- Android package: `com.projectbsds.v49`

The 2026-10-01 APK update redirects to the current laptop-hosted game server
at `192.168.1.103:9339`. It was installed in place on the Xiaomi Pad 6, and
login to the home screen and the laptop's TCP connection were verified over
Wi-Fi. The published battle build also passed live Gem Grab and Bounty win,
result-screen, reward, and reconnect checks. Bounty ended at exactly 20/20
with 1:19 remaining. Individual flying trophy sprites remain unfinished.
For your own installation, discover your game-server computer's current LAN
address and configure the client accordingly; LAN addresses can change.

You can also download it with an authenticated GitHub CLI:

```powershell
gh release download v49.194 -R TerminalDev-1/VibeBSDS-V49 -p VibeBSDS-V49.apk
```

The release asset includes the native battle fixes built by
[`scripts/patch_v49_client.py`](scripts/patch_v49_client.py). Run server checkpoint
`c37019ae9fa4e70cf0ed76940dac6520f496c092` or newer for the matching Battle End
packet. See [`scripts/README.md`](scripts/README.md) for version checks and the
signing workflow; rebuilding requires a compatible original native library.
APK build products remain outside Git.

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


### V49 progression packet findings (2026-10-01)

Native decoder inspection identified separate per-hero scoreChanges,
masteryPoints, and masteryPointChanges arrays in Battle End. At the initial
inspection the server sent zero for scoreChanges and empty mastery arrays.
The later animation checkpoint below records the corrected fields and live proof.

Star Road command 562 opens the claim presentation. Command 560 consumes TWO
data references (brawler and payment resource), rather than the one currently
decoded by the server. Native server command 227 replaces StarRoadData and
notifies its observers; the inherited command 225 label is incorrect for that
purpose. These findings come from native code inspection, not completed unlock
flow verification. Mastery reward command 569 reads a brawler reference, reward
index, and fallback boolean; claimed mastery state is a sequential count.

## Project history

### Current VibeBSDS milestone

- Replaced ephemeral player objects with durable SQLite-backed accounts.
- Added real battle reward persistence and battle history.
- Added trophy, token, credit, Star Road, and brawler-selection logic.
- Added Brawl Pass/token progression plus exact, durable, duplicate-safe credit
  reward claims synchronized into Star Road.
- Rebuilt HomeData and profile data around stored player state.
- Added Gem Grab as the first mode and device-verified Bounty as the second.
- Corrected the V49 Battle End layout, default-skin encoding, winning-team
  conversion, and result team placement. The shared result/reward path persists
  rewards before sending the result and includes a database battle receipt.
- Added reproducible client fixes for Gem Grab Play crashes and Bounty ending
  at 20 points; see `scripts/README.md`.
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

## Mastery progression checkpoint (2026-10-01)

V49 mastery awards now use the asset-defined normal-battle table and the
brawler's pre-battle trophies, independently of the +750 trophy policy, capped
at 24,800 points. Command 569 validates ownership, earned thresholds and
sequential claims in one transaction. Coins, shared power points, credits,
chroma credits and unique mastery cosmetics have durable reward records.
Reward delivery uses command 203; the native claim alone marks the node but
does not add the currency.

On the Xiaomi Pad 6, Shelly's first three earned rewards were claimed once:
750 coins, 100 shared power points and 75 credits. Reconnect showed 1,750 coins,
148 Star Road credits, the shared upgrade resource and the three claimed nodes.
Automated checks cover win/loss/draw awards, thresholds, the cap, invalid and
duplicate claims, decoder alignment and cosmetic persistence. Gold cosmetic reward
presentation still needs live proof; Battle End +5 mastery was subsequently
verified in the live Colt and Bull wins.
Existing mastery totals are retained rather than reset.

## Star Road presentation checkpoint (2026-10-01)

Unlike the upstream BSDS base, VibeBSDS now updates the active credit route
through native server command 227 after an atomic brawler claim. Command 562
requires a reward response; command 560 also carries a payment resource.
Reward command 203 now includes all V49 delivery context and server-base fields.
Its Star Road source is 25. Server command payloads are encoded in a fresh
stream: prefixing their buffer with the command ID while retaining offset zero
made packed booleans overwrite earlier fields, causing an empty-route crash.
Owned mastery vanity references now use the native DataReference format.

Xiaomi Pad 6 proof: Brock unlocked for 160 credits, Barley appeared as the
next target at 13/160 in the same session, and the final Brock reward reveal
closed back to Brawl Pass by tapping. No forced reconnect was needed. The
initial reveal, next-target presentation and delivery reveal remain distinct
client screens. This fixes the trapped flow; it does not remove every reveal.
Database ownership and deduction were verified separately. Cosmetic ownership
serialization follows the native decoder but Gold cosmetic UI proof is pending.
Thirty automated tests, Classes compilation and diff checks passed.

## Battle reward animation checkpoint (2026-10-01)

Battle End now sends the local hero's score change and separate pre-battle
mastery points / mastery gain arrays. Its progression entries are the previous
score and previous HIGH score, not old/new totals. Sending the updated high
score prevented the native rank controller from queuing rank-up effects.
SQLite now captures both brawler and account high scores before updating them.

Live Xiaomi Pad 6 recording (`screenshots/vibe-bull-rank2.mp4`, gitignored):
Bull's win counted from 5 to 755 trophies, played rank-up bursts and showed
+5 mastery at 5/300. Persistence was checked for the awarded progression.
This checkpoint exposed a native presentation defect in large awards: queued
rank-up clips shared their badge state. The later client checkpoint below
records the verified correction.
Individual flying trophy sprites are not yet verified. Do not call the entire
animation finished. Gold mastery cosmetic presentation is also pending;
the 6,000-point daily mastery cap is not implemented.

All 32 regression tests, Classes compilation and diff checks passed. Coverage
includes pre-battle high scores when current trophies are below an earlier
record, and repeated Star Road claims producing no duplicate reward or reload.
These changes use the existing published APK; no replacement asset is needed.

## Large trophy award client checkpoint (2026-10-01)

The V49 client now queues old/new rank badge values with its existing native
rank action before each upgrade clip plays. Previously, creating a +750 reward
sequence repeatedly modified the same clip children, leaving earlier upgrades
with the last rank's badge. The reproducible ARM patch at 0x49c570 fixes that
shared-state ordering without changing the trophy policy or database totals.

Live Xiaomi Pad 6 proof: Brock rose from 5 to 755 trophies; recorded rank-up
bursts showed the appropriate intermediate badges (including ranks 11, 16, 17
and 21), then rank 25 at 755/800. The result also showed +5 mastery at 5/300.
Account trophies increased from 3825 to 4575 and credits from 53 to 73.
Native emulation checks queued old/new badge values at four rank boundaries
and retained the existing Bounty and null-guard behavior. Server checks still
pass all 32 tests. Individual flying trophy sprites remain incomplete.

The tested signed APK uses package com.projectbsds.v49, the existing signing
certificate, and the laptop's rediscovered address 192.168.1.103:9339. Its
SHA-256 is 7742556db316b4867ddf9843d3490bc91ae7c7d53100332b4a6832cb5cbff8b6.
Release publication is recorded separately after upload verification.
