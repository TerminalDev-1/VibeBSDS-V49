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

At least fourteen meaningful improvements were made:

| # | Improvement | Current status |
|---:|---|---|
| 1 | SQLite persistence and schema management | Working |
| 2 | Persistent account identity and tokens | Working |
| 3 | Android-device account recovery | Working |
| 4 | Database-backed HomeData | Working for central player progression |
| 5 | Total and per-brawler trophies | Working |
| 6 | Transactional battle rewards | Working |
| 7 | Persistent battle history | Working |
| 8 | Stored battle credits and Star Road spending | Working; overall credit ecosystem partial |
| 9 | Star Road progression and brawler unlocking | Working |
| 10 | Duplicate Star Road unlock protection | Working |
| 11 | Persistent brawler ownership and selection | Working |
| 12 | Gem Grab plus playable Bounty | Working |
| 13 | Battle End tied to stored progression | Early/partial |
| 14 | Automated regression tests | Working |

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

- Team win: `+8` trophies
- Team loss: `-6` trophies
- Five-trophy client-safety floor
- Placement-based trophy table for Showdown-compatible results
- Matching total-account and per-brawler trophy changes
- Highest-trophy tracking

The database is updated before the Battle End response is sent.

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

## 6. Credits (partially complete overall)

Credits are no longer a purely visual client value. They are:

- Stored in SQLite
- Awarded from completed battles
- Reflected in HomeData
- Preserved across reconnects
- Used as the Star Road spending currency
- Deducted transactionally during a successful unlock

That working core does not make the entire credit ecosystem complete. Brawl
Pass credit rewards still need exact transfer, durable reward-node claim state,
and client synchronization. In short: credits half work in VibeBSDS, while they
hardly worked as progression in base BSDS.

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
- Refreshed HomeData after a successful claim

The core credit-spending and brawler-unlock path works and is tested.

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

## 10. Early Battle End integration

Battle End now connects the reported result to database-backed progression and
returns updated trophy/reward values.

It remains an early implementation:

- The complete result presentation is unfinished.
- The trophy-flying animation has not been implemented.
- Result UI, animation, database changes, HomeData, and reconnect state still
  require separate validation when this area changes.

## 11. Partial Brawl Pass support

The Brawl Pass and token progression are present, but reward claiming is not
complete. Remaining work includes:

1. Registering the exact reward tap and node on the game server.
2. Persisting a durable claimed state.
3. Transferring the exact credit amount into Star Road/the active unlock target.
4. Returning updated state so the client visibly marks the reward claimed.
5. Preventing the same reward from being offered repeatedly.

## 12. Automated regression coverage

The current test suite covers:

- Stable account identity and reconnect behavior
- Persistent battle rewards
- Database integrity
- Two-mode event encoding
- Database-backed HomeData
- Advertised-map reward fallback
- Transactional and idempotent Star Road claims
- Rejection of rewards for unowned brawlers
- Correct V49 character/card mapping around disabled rows

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
- Brawl Pass reward claim synchronization remains unfinished.
- Battle End presentation and trophy animation remain unfinished.

## Authorship

The BSDS protocol foundation is upstream work. All new code paths that moved
VibeBSDS beyond that foundation were generated by OpenAI Codex under
TerminalDev-1's direction, testing, and product decisions.
