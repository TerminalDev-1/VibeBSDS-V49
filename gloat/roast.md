# VibeBSDS V49: The Gloat and Roast File

Welcome to the completely necessary victory lap.

This is affectionate open-source trash talk, not an attempt to erase history.
BSDS gave us the V49 protocol foundation, packet structure, crypto path, and a
client that could reach a home screen. Credit where it is due: without that
foundation, there would be nothing here to roast.

But a foundation is not a finished house. BSDS poured the concrete, placed one
plastic chair in the middle, painted **RANK 1 / 1,250 TROPHIES / POWER 11** on
the wall, and called the estate agent.

VibeBSDS started building the rest of the house.

## The short version

Base BSDS was excellent at saying:

> Here is some HomeData. Please do not ask where it came from.

VibeBSDS can now say:

> Here is your account, your database row, your actual brawler, your battle
> result, your trophy delta, your credits, your Star Road target, your unlock,
> and the same state again after you reconnect.

That is not a reskin. That is a change in what kind of game server this is.

## The improvement scoreboard

We made at least **14 meaningful improvements** beyond the base server.

| # | Base BSDS behavior | What VibeBSDS added |
|---:|---|---|
| 1 | Player state mostly lived for the current session. | A real SQLite database with automatic schema setup. |
| 2 | Accounts behaved like temporary protocol props. | Persistent accounts, IDs, login tokens, and reconnect recovery. |
| 3 | Reinstalling or losing a token could mean losing the player. | Android-device identity recovery reconnects the correct local account. |
| 4 | HomeData presented fixed player values. | Database-backed trophies, currencies, profile values, and progression. |
| 5 | Rank 1, 1,250 trophies, and Power 11 were basically stage scenery. | Actual total and per-brawler trophy state with a client-safe floor. |
| 6 | Battles did not form a durable progression loop. | Transactional trophy, token, credit, win, and loss updates. |
| 7 | Battle history was approximately "trust me, bro." | A persistent battle ledger containing map, result, rank, brawler, rewards, and time. |
| 8 | Credits were decorative UI confetti. | Credits are stored, awarded, spent, and restored after reconnecting. |
| 9 | Star Road looked interesting until it had to do something. | Real targets, credit costs, transactional spending, and brawler unlocking. |
| 10 | Repeated actions had little authoritative protection. | Idempotent Star Road unlock handling prevents duplicate unlock transactions. |
| 11 | Selecting a brawler did not represent durable ownership state. | Database-backed brawler ownership and selected-brawler persistence. |
| 12 | The event experience was Gem Grab Groundhog Day. | Gem Grab first and a genuinely playable Bounty mode second. |
| 13 | Battle End barely had a relationship with progression. | An early Battle End path connected to stored battle rewards and HomeData. |
| 14 | Regressions were discovered by emotional damage. | Automated database, progression, reward, identity, event, and packet tests. |

And yes, the custom client uses its own package, the working APK is preserved as
a release asset, and the official repository includes a durable `AGENTS.md` so
future Codex sessions do not wake up with protocol amnesia.

## Roast round 1: the database

BSDS looked at the concept of durable storage and said, "What if the player
simply never closes the server?"

VibeBSDS added `player.sqlite`, versioned migrations, foreign keys, account
records, brawler records, battle records, and progression-action records.
Player state is no longer a collection of optimistic Python values hoping the
process never ends.

The difference is simple:

- BSDS: the player exists because the server currently remembers them.
- VibeBSDS: the player exists because the database can prove it.

## Roast round 2: hardcoded HomeData

The base server handed everyone the same cardboard identity. Rank 1. A giant
fixed trophy number. Power 11. It was less "player progression" and more "name
badge at a convention."

VibeBSDS rebuilt the important player-facing sections around stored state:

- Total trophies
- Highest trophies
- Per-brawler trophies
- Selected brawler
- Unlocked brawlers
- Power level
- Coins and gems
- Credits
- Profile statistics
- Star Road target

Not every old club or social field has been replaced yet, but the central
player progression is no longer being performed by a ventriloquist.

## Roast round 3: battle rewards

In base BSDS, finishing a battle and expecting meaningful progression was like
putting money into a vending machine that only displayed a picture of crisps.

VibeBSDS now takes the client's completed local/offline bot battle and commits
the result before sending Battle End:

- Team victory: `+8` trophies, 20 tokens, 20 credits
- Team defeat: `-6` trophies, 10 tokens, 8 credits
- Showdown-compatible placement trophy table
- Total and per-brawler trophy updates
- Win/loss counters
- Battle count
- Battle-history entry

Then the player can reconnect and the rewards are still there. Revolutionary
concept: when the game says a number changed, the number remains changed.

## Roast round 4: credits and Star Road

BSDS had credits in the same sense that a movie set has doors: they looked
convincing until somebody tried to open one.

VibeBSDS made the loop real:

1. Battles award stored credits.
2. HomeData exposes the current Star Road target.
3. A claim command reaches the game server.
4. The database checks ownership and the exact cost.
5. Credits are deducted transactionally.
6. The brawler is unlocked.
7. Duplicate unlock transactions are rejected.
8. Fresh HomeData reflects the new account state.

There is still unfinished work around **Brawl Pass credit reward claims**. The
pass can display progress and tokens, but it still needs exact reward transfer,
durable reward-node claim registration, and client synchronization so the same
reward cannot pretend to be claimable forever.

That is the difference between VibeBSDS and wishful documentation: unfinished
work gets named instead of quietly wearing a "works" sticker.

## Roast round 5: events

Base experience:

> Gem Grab refreshed into Gem Grab, which refreshed into the exciting new mode
> called Gem Grab.

VibeBSDS currently advertises two client-proven modes:

1. **Gem Grab — Hard Rock Mine**
2. **Bounty — Shooting Star**

Bounty was verified in a real device match with its arena, star scoreboard,
and bounty indicators. It is not merely a menu card dressed up for screenshots.

We also investigated Brawl Ball far enough to learn exactly how the client
lies. It can show the map, ball-mode scoreboard, and event card while secretly
running Gem Grab's mine and carried-gem behavior. Other event slots open an
endless "Selecting Event" roulette.

So we removed the fake hybrid instead of bragging about a mode that did not
work. Current chance of fixing it: effectively 0%. Chance with a dramatically
stronger future model, something like the hypothetical GPT Astro: perhaps 5%.

Even our failure analysis is more functional than the fake Brawl Ball mode.

## Roast round 6: Battle End

Battle End exists, but nobody is putting it in a tuxedo yet.

The early implementation connects the reported result to durable rewards and
returns progression values. The complete presentation is unfinished, and the
trophy-flying animation has not been implemented.

That makes it partial—but importantly, partial in the direction of real state.
The trophies may not fly across the screen yet, but unlike the old hardcoded
numbers, they do land in the database.

## Roast round 7: tests

Base BSDS testing strategy:

> Launch it. If the client reaches home, resist touching anything.

VibeBSDS has regression coverage for:

- Stable account identity
- Reconnect recovery
- Persistent battle rewards
- Database integrity
- Two-mode event encoding
- Database-backed HomeData
- Advertised-map reward fallback
- Transactional and idempotent Star Road claims
- Rejection of rewards for unowned brawlers
- Correct V49 character/card mapping around disabled rows

The suite is still small, but zero tests no longer has an undefeated record.

## What we are actually proud of

The biggest achievement is not any single menu, packet, or number. It is the
feedback loop:

```text
login
  -> persistent account
  -> database-backed HomeData
  -> local/offline battle
  -> transactional result and rewards
  -> trophies, tokens, and credits
  -> Star Road progress
  -> brawler unlock
  -> refreshed HomeData
  -> reconnect with the same state
```

Base BSDS made the client talk.

VibeBSDS gave the conversation a memory.

## AI disclosure, because we can gloat honestly

The inherited BSDS foundation is upstream work and is not being claimed as
AI-generated. Every new code path that moved VibeBSDS beyond that foundation
was generated by OpenAI Codex under TerminalDev-1's direction, testing, and
product decisions.

That includes the database, progression, trophies, credits, Star Road,
brawler-state handling, Bounty restoration, Battle End integration, and tests.

The code is AI-generated. The failures were real. The device testing was real.
The database is real. The progression persists. And the roast has receipts.

## Final score

BSDS deserves credit for giving V49 a pulse.

VibeBSDS gave it accounts, memory, progression, rewards, unlocks, another mode,
tests, and enough self-awareness to admit when Brawl Ball is still Gem Grab in
a football shirt.

Respect the foundation.

But also respect the renovation.
