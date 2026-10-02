# VibeBSDS V49 Improvements over BSDS

This is the factual companion to [`roast.md`](roast.md). It records what was
actually added beyond the upstream BSDS foundation, what has been verified, and
what remains incomplete.

## Summary

VibeBSDS changed the project from a mostly hardcoded protocol implementation
into a stateful, self-hostable game server with durable accounts and a working
progression loop.

## What the base client actually showed

The comparison starts from a very specific baseline:

- Base BSDS showed Brawl Pass but **no Star Road at all**.
- Every brawler was already unlocked, removing the normal unlock journey.
- Player presentation was hardcoded around Rank 1 and 1,250 trophies.
- Credits hardly formed a usable or persistent progression path.
- Closing or reconnecting did not provide the durable account loop VibeBSDS
  now uses.

The improvements include:

| # | Improvement | Current status |
|---:|---|---|
| 1 | SQLite persistence and schema management | Working |
| 2 | Persistent account identity and tokens | Working |
| 3 | Android-device account recovery | Working |
| 4 | Database-backed HomeData | Working for central player progression |
| 5 | Total and per-brawler trophies | Working |
| 6 | Transactional battle rewards | Working |
| 7 | Persistent battle history | Working |
| 8 | Battle and Brawl Pass credits plus Star Road spending | Working |
| 9 | Star Road progression and brawler unlocking | Durable; same-session transition verified |
| 10 | Duplicate Star Road unlock protection | Working |
| 11 | Persistent brawler ownership and selection | Working |
| 12 | Gem Grab plus playable Bounty | Working |
| 13 | Battle End tied to stored progression | Result/reward screens verified; flying trophy sprites incomplete |
| 14 | Automated regression tests | Working |
| 15 | Offline bot roster and special-skill crash guards | Gem Grab Play and completed matches verified on device |
| 16 | Bounty score limit and match completion at 20 | Verified on device at 20/20 with 1:19 remaining |
| 17 | Reproducible native patches and GitHub APK publication | Tested APK published; uploaded digest matches |

## 1. Persistent SQLite database

VibeBSDS creates `player.sqlite` automatically. The schema is versioned and
contains durable records for:

- Accounts
- Login tokens and Android identity
- Currencies
- Brawler ownership and selection
- Total and per-brawler trophies
- Power and mastery fields
- Battle totals, wins, and losses
- Battle history
- Progression actions

Database changes use transactions for reward and unlock operations. Foreign-key
and integrity behavior is covered by tests.

## 2. Stable account identity and recovery

Players reconnect to stored accounts rather than receiving disposable runtime
state. VibeBSDS supports:

- Persistent account IDs
- Persistent login tokens
- Token-based reconnect
- Android-device identity recovery
- Reloading the complete player/brawler state from SQLite

## 3. Dynamic player HomeData

The major fixed player values from base BSDS were replaced with database-backed
state. HomeData now reflects:

- Current and highest trophies
- Per-brawler trophies
- Selected and unlocked brawlers
- Power level
- Coins and gems
- Credits and other stored currencies
- Profile and battle totals
- Current Star Road target

Some inherited club/social structures remain static and are tracked as future
work. The central player progression path is dynamic.

## 4. Trophy progression

VibeBSDS applies persistent trophy deltas after reported battle completion:

- Team win: `+32` trophies
- Team loss: `0` trophy change
- Five-trophy client-safety floor
- Placement-based trophy table for Showdown-compatible results
- Matching total-account and per-brawler trophy changes
- Highest-trophy tracking

The database is updated before the Battle End response is sent.


The October 1 trophy-policy update changes team wins from +8 to +750 trophies
and defeats from -6 to zero trophy loss. Tokens and credits retain their
existing amounts; draws and the unadvertised Showdown placement table are
unchanged. A live Bounty win displayed Victory +750, raised account trophies
from 60 to 810 and Shelly from 55 to 805, and retained both values after
reconnect. Zero-loss defeats on either team are covered by regression tests,
not a separate live defeat. This server change works with the published APK.

## 5. Battle rewards and history

Completed local/offline bot battles now feed a durable reward path:

- Trophies
- Brawl Pass tokens
- Credits
- Win/loss counters
- Battle count
- Map and brawler attribution
- Persistent timestamped battle ledger

Results are restored into HomeData after returning home or reconnecting.

## 6. Credits

Credits are no longer a purely visual client value. They are:

- Stored in SQLite
- Awarded from completed battles
- Awarded in the exact amount from known V49 Brawl Pass credit nodes
- Reflected in HomeData
- Preserved across reconnects
- Recorded per pass season, track, and tier so a node cannot pay twice
- Used as the Star Road spending currency
- Deducted transactionally during a successful unlock

The game server acknowledges successful credit claims with V49's delivery-item
server command. This updates the live client without the crash caused by
injecting a second full HomeData packet into an established session.

## 7. Star Road

VibeBSDS added the V49.194-specific Star Road data and command path:

- Rarity-grouped unlock candidates
- Credit costs and gem alternatives
- Current and queued targets in HomeData
- Server-side validation of the requested brawler
- Credit-balance validation
- Transactional credit deduction
- Persistent brawler unlock
- Duplicate/unowned-state protection
- Correct next target after reconnect

The credit-spending and brawler-unlock path advances to the next target in
the same session. The V49 reward reveal now dismisses without reconnecting.
Gem purchases remain unsupported server-side.

This was not a repair of an already visible base feature: base BSDS displayed
no Star Road at all and started with every brawler unlocked. VibeBSDS added the
actual Star Road presentation and progression path.

## 8. Persistent brawler ownership and selection

The game server stores which brawlers an account owns and which brawler is
selected. Selection commands are validated against ownership and survive
reconnects.

The V49 character/card mapping also accounts for disabled, non-contiguous
character rows instead of incorrectly renumbering later brawlers.

## 9. Two client-proven events

The stable event list is:

1. Gem Grab - Hard Rock Mine
2. Bounty - Shooting Star

Both remain on the client-safe event slot. Their instance IDs preserve the
requested chooser order. Bounty was verified on the Android device with its
correct arena, star scoreboard, and bounty indicators.

## 10. Shared Battle End result and reward flow

Compared with the base server's static presentation, Battle End now connects
the reported result to transactional database progression and displays the
result and reward screens for Gem Grab and Bounty.

The October 1, 2026 update corrected the V49 packet layout, default-skin
encoding, and hero display/footer fields. Incoming winning-team IDs are
normalized relative to the local player, and result-screen sides are encoded
as allies/enemies relative to that player. Each stored battle supplies a
database receipt; pre-battle trophies and pre-battle score/high-score snapshots allow the
client's trophy bar and token counter to animate.

The earlier October 1 live Gem Grab and Bounty wins reached the result/reward
screens under the previous reward policy, awarded +8
trophies, 20 tokens, and 20 credits, and retained progression after reconnect.
Gem Grab trophies also survived app/server restarts. Defeat/draw, placement,
and either-team normalization are covered by regression tests; those outcomes
were not separately verified in live matches.

Remaining limits:

- Individual flying trophy sprites have not been implemented.
- Offline requests omit kills, damage, healing, and MVP data, so those result
  statistics remain empty.
- Result UI, animation, database changes, HomeData, and reconnect state still
  require separate validation when this area changes.

## 11. Brawl Pass credit rewards

The Brawl Pass and token progression are present. Credit rewards now:

1. Decode the exact reward track, season, and tier claimed by the client.
2. Persist a durable claimed-state receipt.
3. Transfer the exact configured amount into Star Road.
4. Send the credit delivery-item acknowledgement to update the live client.
5. Reject duplicate claims transactionally.

Other Brawl Pass reward types remain incomplete.

## 12. Automated regression coverage

The current test suite covers:

- Stable account identity and reconnect behavior
- Persistent battle rewards
- Database integrity
- Two-mode event encoding
- Database-backed HomeData
- Advertised-map reward fallback
- Transactional and idempotent Star Road claims
- Exact and idempotent Brawl Pass credit claims and claimed-node masks
- Encrypted post-login command framing
- Rejection of rewards for unowned brawlers
- Correct V49 character/card mapping around disabled rows
- Player-relative win/loss conversion, draw/placement preservation, and battle receipts
- Complete V49 result packet layout, default skins, and pre-battle score/high-score snapshots

The October 1 checkpoint passed all 19 tests. The optional native verifier
executes the actual patched ARM32 code to check the Bounty threshold, other-mode
isolation, existing-winner preservation, and null roster/special-skill guards.

Run it with:

```powershell
python -m unittest discover -s tests -v
```

## 13. Client and release safety

- The custom Android package is `com.projectbsds.v49`.
- The verified client is preserved as the `VibeBSDS-V49.apk` release asset.
- APKs, databases, logs, builds, signing material, and screenshots are excluded
  from normal Git history.
- Runtime-visible changes are validated on the actual Android device instead of
  being declared complete from packet encoding alone.

## 14. Offline client crashes and the Bounty score limit

The earlier compatible client could crash when offline bots lacked a roster
for passive/gadget setup. A special-skill callback could also replace its actor
with a null return before reading its position. Native guards now handle absent
rosters and skip the null callback while retaining the actor. Gem Grab Play
reached Hard Rock Mine and completed its match and reward flow on Xiaomi Pad 6.

Bounty already declared MaxScore=20 in its CSV, but its offline controller
continued beyond that value. The native patch caps score reads at 20 and sets
the existing winner field for variation 3, entering the normal result flow.
Live evidence recorded exactly 20/20 with 1:19 remaining, then the victory
screen. Other variations retain their existing score behavior.

Reproducible patching and ARM32 verification scripts are documented in
[scripts/README.md](scripts/README.md). Rebuilding requires a compatible original
V49.194 native library; unsupported hashes are rejected.

The tested build is published as the
[VibeBSDS-V49.apk release asset](https://github.com/TerminalDev-1/VibeBSDS-V49/releases/download/v49.194/VibeBSDS-V49.apk).
Its SHA-256 is
`7742556db316b4867ddf9843d3490bc91ae7c7d53100332b4a6832cb5cbff8b6`;
GitHub's uploaded digest matches the installed build. Use server checkpoint
`c37019ae9fa4e70cf0ed76940dac6520f496c092` or newer for its Battle End packet.
The release redirects to `192.168.1.103:9339`; discover and configure your own
server's current LAN address. The matching certificate allowed an in-place
update of `com.projectbsds.v49` with app data retained.


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

## Evidence and development method

The improvements were not inferred only from source code or menu rendering.
OpenAI Codex performed live testing through wireless Android debugging on the
Xiaomi Pad 6, including:

- Installing and relaunching the isolated `com.projectbsds.v49` client
- Connecting it to the local game server over Wi-Fi
- Opening the event chooser and verifying Gem Grab/Bounty ordering
- Entering matches and inspecting the real mode scoreboard/controller
- Rejecting the fake Brawl Ball/Gem Grab hybrid after arena inspection
- Exercising Battle End and returning home
- Reconnecting to verify database-backed trophies and progression
- Capturing device screenshots under the gitignored `screenshots/` directory

Codex accelerated the work by keeping code changes, packet analysis, game
server restarts, automated tests, wireless-device actions, and visual evidence
inside one iterative workflow. No exact speed multiplier is claimed, but the
feedback cycle was materially shorter than a manual handoff between separate
coding, deployment, and device-testing stages.

## Known boundaries

- Battles are client-side local/offline bot simulations, not a
  server-authoritative real-time multiplayer engine.
- Brawl Ball is not playable with the current implementation.
- A Brawl Ball-looking hybrid still runs Gem Grab behavior and is not shipped.
- Alternative event slots can trigger the client's endless event roulette.
- Some inherited club and social values remain static.
- Some brawler-specific behavior/content remains unfinished.
- Non-credit Brawl Pass reward types remain unfinished.
- Individual flying trophy sprites and detailed combat statistics remain unfinished.

README.md and improvements.md are updated together for each verified change or
substantial investigation before committing and pushing its checkpoint. Each
entry records improvements over base BSDS, evidence, and remaining limitations.

## Authorship

The BSDS protocol foundation is upstream work. All new code paths that moved
VibeBSDS beyond that foundation were generated by OpenAI Codex under
TerminalDev-1's direction, testing, and product decisions.

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
Release publication and uploaded-digest verification are recorded below.

## Rank-update APK publication (2026-10-01)

The tested rank-animation APK replaced the v49.194 GitHub Release asset
VibeBSDS-V49.apk. GitHub reports SHA-256
7742556db316b4867ddf9843d3490bc91ae7c7d53100332b4a6832cb5cbff8b6,
matching the signed/installed build (479,200,690 bytes). Use server checkpoint
de710ca493ff4858e3cf314c8e993faa5ed596e8 or newer. The existing download link
remains valid. Release notes now describe mastery progression, the dismissible
Star Road reveal and sequential rank-up badges, with their remaining limits.

An in-place install retained account data. Reconnect showed Brock at rank 25,
755/800 trophies and 5/300 mastery, matching SQLite. The server laptop's runtime
IPv4 remains 192.168.1.103 and the client redirects to port 9339. Other
self-hosters must configure their own current address. The prior battle-fix
APK is superseded; build products and signing files remain gitignored.

## Correct outcome field and +32 policy (2026-10-01)

Team wins now award +32 trophies; defeats and draws change trophies by zero.
The inherited Showdown placement table is unchanged while playable Showdown is
investigated. Existing account/brawler totals are preserved.

Native inspection corrected the earlier packet interpretation: 0x54c5d0
writes the player-relative outcome (0 win, 1 loss, 2 draw) to arena+0xd4;
0x54c6e4 encodes that as the FIRST integer of 14110. The second integer comes
from arena+0xa0 and identifies the local team. Comparing the second integer
with hero.Team made completed defeats look like victories and awarded trophies.
The server now reads Outcome from the first integer and uses it for stored
rewards and the outgoing result. Hero ally/enemy display remains team-relative.

This invalidates earlier claims that matching Result and hero.Team proved a
win. Prior rank/counting recordings still prove those animations and saved
totals, but not the correctness of the displayed victory. Native evidence and
33 tests verify the corrected mapping, zero loss, +32 wins, both local teams,
draws, decode/execute of a real-shaped defeat and no defeat mastery award.
Live outcome proof is pending at this checkpoint; a pre-existing native Play
crash interrupted the first attempt. No replacement APK is required.

## Subsequent live defeat and Showdown verification (2026-10-01)

The corrected server produced **DEFEAT / 0 trophies** for a real lost Gem Grab
match on the Xiaomi Pad 6. Its receipt contains Outcome=1/local team=1, and
SQLite battle 15 records result=1, trophy_delta=0, 10 tokens and 8 credits.
Reconnect preserved account trophies 4575 and Shelly trophies 1555; credits
advanced from 73 to 81. The probe hid shared power points only in HomeData to
get past the client's upgrade tutorial, without changing stored balances or
battle logic. The normal server retains the actual balance.

A temporary Solo Showdown event (slot 1/index 33/map 13/variation 6) displayed
Skull Creek, but Play crashed in the native bot-profile path (PC 0xdcdeb0,
invalid pointer 0x6e756f72). No ten-player arena, survival rules or placement
result was proven. The normal event list still contains Gem Grab and Bounty.
Showdown and upgrade/tutorial handling remain incomplete.

The v49.194 release notes now describe the corrected outcome, +32 team wins and
live zero-loss defeat proof. No APK replacement was needed. Normal Core.py was
restored with real shared power points, and scripts/README.md now records the
correct first-outcome/second-local-team packet fields.

### Showdown native profile investigation

Actor profile lookup 0x61a2c8 lacks an upper-bound check; its existing fallback
is 0x61a844. A five-case ARM probe passed and the live attempt progressed to
a different UI null-profile crash at 0x44eb4c. Its fallback is 0x44ebe8; a
second bounds/null guard passes five emulation cases. These guards remain
experimental until live arena/results succeed. No Showdown release claim or
APK publication has been made for this investigation.


### Showdown arena guard checkpoint (2026-10-01)

Two native profile-vector guards now preserve the existing missing-profile and
unskinned actor paths. Unlike the upstream BSDS client, the experimental build
reaches a ten-player Solo Showdown arena on Skull Creek (map 13, variation 6),
with power-cube boxes and closing poison. Xiaomi Pad 6 evidence is stored in
`screenshots/showdown-two-guards-real.png` and `showdown-arena-check.png`.
The first native result submitted rank 9 with ten heroes. Result presentation
and zero-loss placement rewards still need work; Showdown is not yet enabled
in the public event list, and the release APK is unchanged. Ten ARM emulation
cases cover valid indices, overflow and null UI profiles.


### Solo placement reward checkpoint (2026-10-01)

Showdown results now store win/loss independently of the local team. First
place earns +32 trophies; placements 2-5 retain +8/+6/+4/+2, and placements
6-10 lose zero trophies. The outgoing survival result uses gametype 2 and
the actual placement. Invalid placements above ten are rejected.
All ten placements are regression-tested for saved rewards and outcome.
Live placement 9 (SQLite battle 19) preserved account trophies at 4563 and
Shelly at 1543 after returning home; screenshot `showdown-exit-game2.png`
records that state. Earlier experimental matches used the inherited negative
table and are retained in history. Reward-screen presentation remains pending
because the offline client waits for the remaining bots. Public events and
the release asset are still unchanged.


### Showdown result transition investigation (2026-10-01)

Native `0x2a3490..0x2a34e8` only schedules the Solo Showdown result transition
after a result is pending, variation is 6, and the remaining actor count is
at most one. This explains the eliminated-player practice overlay despite
a saved placement. An experimental APK removes the final count branch at
`0x2a34c8`; it is installed but has NOT passed a live match test. Its SHA-256
is `849ba79462b10ea5a47421d2dcf509bbf8f9dba19301d3c15908dac5a41899db`.
The code change remains outside tracked source and the public release.
Wireless ADB disconnected after the in-place install. The tablet still
responded at its runtime LAN address, but no ADB service was advertised and
its previous endpoint refused connections; no high-port listener was found.
The normal Core.py server was restored with Gem Grab/Bounty and the real
shared power-point balance. A live Showdown reward screen, cube pickup,
first-place reward/reconnect, and normal-mode regression are still required
before enabling Showdown or publishing its APK. The committed reproducible
guard patch matches the live-tested arena library byte for byte.
When device access returns, restore Android `stay_on_while_plugged_in` to its
original value 0 after testing. It was temporarily enabled while charging.
The experimental APK could not be replaced while ADB was unavailable.


### Showdown device reconnection checkpoint (2026-10-02)

Direct multicast DNS discovery found the tablet again after its wireless ADB
port changed; the stored endpoint was obsolete. Runtime discovery remains
required. The installed APK digest matches the unpublished transition probe
`849ba79462b10ea5a47421d2dcf509bbf8f9dba19301d3c15908dac5a41899db`.
The laptop server established a TCP session with the tablet. A new Solo match
submitted placement 7 with ten heroes; SQLite battle 20 records result 1,
zero trophies, 10 tokens and 8 credits. Home retained account trophies 4563
and Shelly 1543 (`screenshots/showdown-oct2-after-transition.png`).
The reward screen remains unverified: the observed flow returned home, and a
subsequent launch ended with SIGFPE in a WebView/Frida thread. The crash log is
`screenshots/showdown-oct2-crash.txt`; this does not establish a game-library
root cause or a fix. Do not publish the transition probe or enable Showdown
based on these observations. Device controls await clarification about
whether TerminalDev-1 is actively using the tablet.


### Solo first-place persistence (2026-10-02)

Live Solo Showdown submitted rank 1 with ten heroes (SQLite battle 21).
It stored result 0, +32 trophies, 20 tokens and 20 credits. Account trophies
4563 -> 4595 and Shelly 1543 -> 1575 survived reconnect; evidence is
`screenshots/showdown-first-reconnect.png`. The arena also showed power-cube
drops and closing poison, but cube pickup and the reward screen are not yet
proven. The practice exit still bypasses the presentation.
Native incoming-result dispatch stores the new result at instance+0x3e8,
while the end overlay refuses to open when instance+0x3b4 is already set.
An unpublished receipt probe resets that flag while preserving the handler
return value; ARM emulation passes. This remains a hypothesis awaiting live
verification, not a published fix. User permission to control the tablet has
resumed; runtime ADB is connected.


### Solo result-screen checkpoint (2026-10-02)

The native receipt handler now clears the prior end-screen state at
`0x431364`, retaining its zero return. The Solo pending-result branch at
`0x2a34c8` no longer waits for all remaining bots. The live Xiaomi Pad 6
first-place result displayed "You are #1!", +32 trophies, Shelly at 1607,
+100 mastery and 20 tokens (`screenshots/receipt-probe-current.png`).
The Exit button advanced into the pending Barley credit unlock. The
reproducible patch matches this
installed library byte for byte; native emulation retains earlier guards,
Bounty and rank behavior and checks result flags/counts. Eliminated-player
presentation, cube pickup and normal-mode live regression remain pending.
Showdown stays outside the public event list and this APK is not published
until those checks are complete.


### Solo elimination reward screen checkpoint (2026-10-02)

Unlike the upstream BSDS base, the patched V49 client now opens the native
placement result after elimination as well as first place. Live second-place
proof displayed Rank: 2, +8 trophies, 10 tokens and unchanged mastery.
SQLite battle 23 records rank=2, result=1 and trophy_delta=8; Home showed
Shelly at 1615, account trophies 4640 and credits 9. Evidence is
`screenshots/solo-second-rewards.png` and `solo-second-home.png` (gitignored).
The first-place Exit had advanced into the pending Barley credit claim, rather
than directly to Home; both reveal stages were dismissed and Home returned
with El Primo as the next credit target. Lower-placement reward-screen proof,
cube pickup and existing-mode regression remain pending. Showdown remains
outside the public event list and the release APK is unchanged.


### Showdown actor-name guard investigation (2026-10-02)

A later Play attempt crashed at native `0x6e3244`, reading a missing profile's
name (`null + 0xec`). Caller `0x241f8c` already permits a null profile when its
owner index falls outside the vector; its existing skip path is `0x241fe8`.
The reproducible patch now routes missing names to that path and preserves
the original getter for present profiles. Two ARM emulation cases pass; the
additional guard still needs live proof. It uses the two padding words after
the passive stub and the final two executable-page words, without growing
into the next ELF segment.

Live fifth place showed Rank: 5 and +2; SQLite battle 24 stores that delta.
Battle 25 records ninth place and zero trophy change, with Home still showing
4642 account trophies. The ninth-place screen was not captured. TerminalDev-1
helped play those matches, then handed gameplay controls back to Codex.
Independent repeated Play crashes have a WebView/Frida SIGFPE stack; they are
not explained or fixed by this actor-name guard. Logs/evidence remain under
`screenshots/` and outside Git. Cube pickup, normal-mode regression and final
release publication remain pending; public Showdown is still disabled.

Experimental signed APK SHA-256:
`14ca420853d26607788550c8c8cd6a1ce0723ceefdb665955852b76530b4fc9d`.
All 34 server tests, Classes compilation and diff checks passed.


### Existing-mode regression and shared crash investigation (2026-10-02)

The actor-name build reached a live Gem Grab match; SQLite battle 27 stores a
win, +32 trophies, 20 tokens and 20 credits. Home showed 4674 account trophies
and Shelly 1649. Its result screen was not captured. Bounty also hit the
WebView/Frida SIGFPE stack before starting, so that stack is not specific to
Showdown and does not establish a Showdown roster cause.

A temporary diagnostic APK changes the Frida signal-forwarding path solely
to expose the original fault address if another exception occurs. It must
NOT be published, and must be replaced with a normal signed build after the
investigation. Its signed SHA-256 is
`a7ac103ab2f45b0fa201e8388cdd472225c6582296a59d9e1c9ed9a0aaaa083d`.
The instrumentation passed native emulation. No source gameplay fix is
claimed from this diagnostic change. That build completed two Bounty defeats:
screenshots `diagnostic-bounty-end.png` and `diagnostic-now.png` show DEFEAT
and 0 trophies, and SQLite battles 28/29 each store result=1, trophy_delta=0,
tokens=10 and credits=8. This adds live zero-loss Bounty proof beyond the
upstream BSDS foundation; it is not final release-build regression proof.

Showdown, final normal-mode verification and APK publication remain pending.
The test server still temporarily hides shared power points to bypass the
upgrade tutorial; restore normal Core.py with the true balance after testing.
Restore Android stay_on_while_plugged_in to 0 after device tests.


### Normal Showdown client result proof (2026-10-02)

The temporary fault-address diagnostic APK was replaced in place with the
normal actor-name-guard build (SHA-256
`14ca420853d26607788550c8c8cd6a1ce0723ceefdb665955852b76530b4fc9d`).
On the Xiaomi Pad 6 this build entered Skull Creek with ten players, survived
to first place, displayed "You are #1!" and +32, then showed Shelly at 1,713
trophies, +100 mastery (2,056/2,600) and 20 tokens. Exit returned to Home.
SQLite battle 31 records map 13, rank 1, result 0, +32 trophies, 20 tokens and
20 credits. Reconnect retained account trophies 4,738, Shelly 1,713 and
109 Star Road credits. Evidence: screenshots/normal-solo-start.png,
solo-position.png, solo-cube-attempt.png, solo-normal-rewards.png and
solo-reconnected-home.png (all gitignored).

This adds live result/reconnect proof for the normal experimental client
beyond the upstream BSDS behavior. The name guard was exercised through a
completed arena, but intermittent Play crashes remain unresolved. Power-cube
pickup/counter proof is still missing; boxes alone do not establish it.
Showdown remains outside the public event list and the GitHub release asset
is unchanged. The local probe still hides shared power points for the known
upgrade tutorial issue; restore normal Core.py and the real balance after
testing. The installed APK no longer contains the temporary fault diagnostic.

### Play-crash signal origin (2026-10-02)

A temporary native signal logger captured the original SIGFPE before Android's
WebView handler forwarded it. Binary logcat records identify libc tgkill at
0x9dddc and its caller in **libfmod.so at 0xdc288**, the return from its
exported divide-by-zero helper calling raise(8). The saved frame points to
libg.so 0x24dd18, following the actor-renderer constructor call. A subsequent
stack-return trace identified libg.so 0x242628, immediately after the renderer
calls signed division at 0x242624. FMOD supplies that arithmetic helper; its
presence does not establish an audio fault. The earlier audio-path inference
is superseded by this renderer division evidence. Do not suppress every SIGFPE. The apparent WebView
origin in ordinary crash reports is a subsequent handler, not the initial
raiser. Evidence: screenshots/callers-crash-log.txt (gitignored).

This is a verified investigation beyond the upstream BSDS client, not a crash
fix. Diagnostic APKs remain gitignored and unpublished. The current temporary
stack-caller build is SHA-256
9387acbc3099a150f9979aab7cef6043352a008d7ba9972ad4122d322dc40bc2;
restore the normal experimental client after tracing. Two more diagnostic
Showdown matches reached first (+32) and third (+6) place, but power-cube
pickup is still unverified. Public events and the GitHub APK asset are unchanged.

### Renderer guard and user-assisted Showdown checkpoint (2026-10-02)

Native signal traces identified zero-divisor calls at libg.so 0x242624
(renderer setup) and 0x248544 (frame update), returning through FMOD's
exported arithmetic helper. This supersedes the earlier audio-fault inference.
A live null-profile crash at 0x450254 exposed another unchecked UI vector
lookup. The reproducible patch adds zero-divisor guards to both health-frame
paths and uses the existing no-profile path for negative/out-of-range indices
and absent entries. Eight division cases and six additional profile cases
pass ARM emulation, alongside the earlier native checks.

The setup-divisor/profile build reached a ten-player arena and a Rank 5 result
with +2 trophies and Exit to Home on Xiaomi Pad 6. Its next Play attempt
exposed the frame-update division. The combined two-divisor build is an
experimental checkpoint awaiting a live match; do not describe all Play
crashes as fixed. Public events and the GitHub release asset are unchanged.
All 34 server tests, Classes compilation and diff checks pass.

TerminalDev-1 clarified that they helped control matches because ADB taps
were slow, and personally confirmed power-cube pickup works. Record pickup
as user-tested gameplay evidence. Codex did not capture the cube counter or
health increase; that visual evidence is not required by the user. Do not
attribute the assisted movement to an AI controller or Auto Clicker. The
Auto Clicker app was temporarily force-stopped during isolation, without
uninstalling it; its involvement was not established. A temporary control-mode
0 probe was inconclusive because matches were user-assisted. Normal HomeData
retains control mode 2. Existing live arena, poison, placement/reward and
reconnect evidence remains valid, with user assistance explicitly credited.

Testing stopped at the user's request. Normal Core.py was restored with
Gem Grab/Bounty and real shared power points; its listener is 0.0.0.0:9339.
Android charging stay-awake was restored to its original value 0. The normal
name-guard experimental APK was restored in place without temporary signal
hooks and with account data retained (SHA-256
14ca420853d26607788550c8c8cd6a1ce0723ceefdb665955852b76530b4fc9d).
Next session: live-test both health guards, repeat normal-mode regression on
the final client, then enable Solo and publish its signed APK as a release
asset when stable. Keep binaries, signing material, logs, databases and
screenshots gitignored. The public release remains the previously published
7742556db316b4867ddf9843d3490bc91ae7c7d53100332b4a6832cb5cbff8b6 build.
