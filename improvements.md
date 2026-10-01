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

- Team win: `+750` trophies
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
database receipt; pre-battle trophies and old/new progression values allow the
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
- Complete V49 result packet layout, default skins, and old/new reward values

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
`1b22ab6c97a8ed894af5f9918fed4c5fd93af4bab83203b97097921f8eaa28bb`;
GitHub's uploaded digest matches the installed build. Use server checkpoint
`c37019ae9fa4e70cf0ed76940dac6520f496c092` or newer for its Battle End packet.
The release redirects to `192.168.1.103:9339`; discover and configure your own
server's current LAN address. The matching certificate allowed an in-place
update of `com.projectbsds.v49` with app data retained.


### V49 progression packet findings (2026-10-01)

Native decoder inspection identified separate per-hero scoreChanges,
masteryPoints, and masteryPointChanges arrays in Battle End. The existing
server sends zero for scoreChanges and empty mastery arrays, even when the
headline reward changes. These are candidates for restoring the client effects;
visual fixes still require live verification.

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
duplicate claims, decoder alignment and cosmetic persistence. Cosmetic reward
presentation and new Battle End mastery animations still need live proof.
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
