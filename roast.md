# BSDS, Please Take a Seat

BSDS is what happens when a login packet succeeds and everybody immediately
clocks out.

It got a V49 client to the home screen, looked at the same hardcoded numbers
staring back, and apparently decided persistence was a problem for another
generation. It was less of a game server and more of a cardboard cutout holding
a TCP socket.

The serious list of everything VibeBSDS added lives in
[`improvements.md`](improvements.md). This file has one job: violence against
hardcoded software behavior.

## The account system: object permanence sold separately

BSDS stored player progress with the same long-term strategy as writing a phone
number on a foggy bathroom mirror.

Close the process and suddenly the server developed selective amnesia. Your
"account" was whatever a Python object happened to remember before the lights
went out. Database? No. Ledger? No. Durable identity? The server barely had a
durable attention span.

VibeBSDS added SQLite because "please never restart the server" is not an
account system. It is a hostage situation.

## HomeData: one identity, every customer

Rank 1. 1,250 trophies. Power 11.

Everybody got the same numbers because BSDS did not serve player progression;
it served the developer's favorite constants. The profile was not a profile.
It was a stock photograph of a profile.

It also unlocked every brawler immediately, because building an unlock path
would have required the progression system to progress. Everybody was Rank 1,
everybody was sitting on the same 1,250-trophy fiction, and every brawler was
already waiting in the wardrobe. The account journey began at the finish line
and still somehow went nowhere.

You could win, lose, reconnect, reconsider your life choices, and the server
would still proudly hold up the same cardboard sign. It had all the dynamism of
a restaurant menu laminated in 2009.

VibeBSDS asked the radical question: what if the numbers on the screen belonged
to the player looking at them?

## The economy: Monopoly money had stronger backing

BSDS credits were decorative purple vapor. They barely worked, generated a tiny
moment of hope, and then vanished the second anyone expected accounting.

Coins, trophies, credits, rewards—it was an economy administered by a magician
whose only trick was making state disappear.

No transaction. No durable balance. No history. Just packets confidently
announcing financial events that the server itself would forget before lunch.

VibeBSDS put the numbers in a database. Our overall credit path is still only
partly finished—battle-earned credits and Star Road spending work, while Brawl
Pass credit claims do not yet synchronize correctly—but "half working" is
still an awkwardly decisive victory over "hardly working at all."

## Star Road: more of a painted line on the floor

Actually, base BSDS did not even get far enough to call it Star Road. **Star
Road did not appear at all.** The home screen had Brawl Pass and every brawler
was already unlocked, so the entire V49 unlock journey had been solved by
deleting the journey.

No road. No target. No meaningful credit destination. Just Brawl Pass standing
alone next to an account that had apparently completed progression before it
was created.

VibeBSDS made credits persist, made costs matter, made unlocks transactional,
and made duplicate unlocks fail. The groundbreaking innovation was remembering
that a brawler had already been unlocked.

## Battle rewards: thank you for playing, nothing happened

Base BSDS could finish a battle with all the economic impact of closing a
YouTube video.

Where did the trophies go? Nowhere.

Where did the credits go? Also nowhere.

Was the win recorded? The server declined to comment.

Battle history was essentially oral tradition. If you remembered winning, that
was the database.

VibeBSDS now records the result, trophies, tokens, credits, wins, losses,
brawler progress, map, and time. The rewards survive reconnecting, an advanced
feature known elsewhere as "not lying."

## Event rotation: Gem Grab has been renewed for 900 seasons

BSDS event scheduling had range:

1. Gem Grab
2. Gem Grab, but later
3. Gem Grab after the timer refreshes
4. You will never guess: Gem Grab

The event timer was not rotation. It was a countdown to the same answer.

VibeBSDS added Bounty, giving the server a second verified mode and increasing
its playable-mode diversity by an astonishing 100%. Competition authorities
are monitoring the situation.

## Battle End: the battle ended before the feature began

The old Battle End experience had the confidence of a finished system and the
follow-through of a New Year's resolution.

VibeBSDS has an early Battle End path tied to actual stored progression. It is
still incomplete and the trophy-flying animation does not exist yet—but at
least the trophies land in the database. BSDS could not make them fly or land.
It mostly watched them leave.

## Testing: the user was the test suite

BSDS quality assurance was beautifully efficient:

> Did the client reach home?
>
> Yes.
>
> Excellent. Nobody touch anything.

Zero regression tests meant every feature had the excitement of live theatre.
Any packet could improvise. Any reconnect could become the season finale.

VibeBSDS added tests for identity, persistence, rewards, Star Road, HomeData,
events, ownership, and database integrity. Nine tests is not enormous, but it
is nine more than the previous strategy of sustained eye contact with the
terminal.

Codex also tested the client on the Xiaomi Pad 6 through wireless Android
debugging: installing the isolated package, restarting the game server,
entering real bot matches, inspecting the mode controller, checking Battle End,
and reconnecting to verify stored state. The work moved quickly because code,
server restarts, packet changes, screenshots, and device feedback stayed in one
tight Codex-driven loop instead of being handed between disconnected tools.

## Brawl Ball: even we found the client's comedy routine

We are not claiming victory here. V49 can dress Gem Grab in a Brawl Ball shirt,
show a football scoreboard, load the right map, and then spawn a gem mine in
the middle like nobody will notice.

Other event slots launch an endless "Selecting Event" roulette. The client
literally spins forever rather than commit to Brawl Ball. Honestly, it learned
that behavior from the base server's relationship with persistence.

We removed the fake hybrid instead of listing it as working. Current chance of
a real fix: effectively zero. Chance with a dramatically stronger future model:
perhaps 5%. Unlike the hardcoded trophy count, that number is at least honest.

## Final diagnosis

BSDS was a protocol skeleton wearing HomeData as a hat.

It could connect. It could display. It could emit packets. Then the moment you
asked it to remember, progress, account, rotate, reward, unlock, or prove
anything, it stared into the middle distance and returned another constant.

VibeBSDS did not merely add features. It introduced the server to consequences.
Battles affect accounts. Credits affect Star Road. Unlocks affect ownership.
Reconnects preserve state. Tests notice when something breaks.

We still have unfinished clubs, partial Brawl Pass claims, incomplete Battle
End presentation, and brawlers whose specific behavior is not finished. The
difference is that VibeBSDS lists unfinished logic as unfinished instead of
unlocking everything, hardcoding the numbers, and hoping nobody asks a second
question.

BSDS got the client through the front door.

VibeBSDS discovered there was supposed to be a building behind it.

Thank you for the foundation.

Please stop calling the plastic chair a furnished house.
