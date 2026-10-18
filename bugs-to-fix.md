# Bugs to fix

Open, user-reported or observed defects for future VibeBSDS sessions. Read this
together with [AGENTS.md](AGENTS.md) before starting new work. Keep each entry
factual: what was seen, on which build, what is known, and what is only
suspected. Move an entry to the "Fixed" section, with its evidence, once it is
verified live. Do not delete it.

## Open

### 0. Release rollback and crashes on the division-wrapper build (2026-10-18)

TerminalDev-1 asked for the `349a44b7...` release (hidden Edit Controls,
global zero-safe division, row-bounds and extra tile guards) to be pulled
immediately. The `v49.194` asset was restored to the previous public build
`45b16d350b4e2233dee52507998810398411d082c5162ed51d9cdca2ab721eaa`, and its
notes carry a rollback notice. GitHub's digest matched after the restore.
The tablet still runs the withdrawn build's port-9340 twin (`63221dd7...`).

Reported on that build:

- **Everything starts flying as soon as a match loads** (see entry 1).
- **A crash during the startup Brawl Stars logo**, before reaching Home. It is
  not in the crash buffer read at 21:30, so no native evidence yet. Capture it
  with `adb logcat -b crash` (or the crash-logging gadget) next time.
- **Continued in-match crashes.** Two were logged (`screenshots/port-9340-health/crash-10.txt`):
  - 21:30:04, uptime 313 s: SIGSEGV null+0xc at `libg.so 0x60e850`, from
    actor UI `0x451d10`, then `0x247b68`, then the renderer loop `0x24dc6c`.
  - 21:30:32, uptime 24 s: SIGSEGV null+0x4 at `libg.so 0x246d34`, directly
    from the renderer loop `0x24dc6c`.
  These are the same broken-actor family as the nine guarded sites. Per-site
  guarding is not converging; fix the spawn/profile root cause instead.

Keep the hidden Edit Controls button (`0x296f04` + `0x2a68f8`); it worked live.
Re-evaluate everything else in the withdrawn build before publishing again.

### 1. Solo Showdown arena chaos after the 2026-10-18 crash guards

Reported by TerminalDev-1 on 2026-10-18 after playing the guarded client
(public release `349a44b7...`; tablet twin `63221dd7...` on port 9340). The
client no longer crashes, but the match looks broken:

- **Brawlers and boxes "flying everywhere"**: actors and power-cube boxes move
  or jump erratically instead of staying put or moving normally.
- **Power-cube box rings disagree**: one box showed a **blue** ring while
  another stayed **red**. Normally all boxes share one style.
- **A bot (shown as "BB") with a shield showed endless healing**: floating
  heal/health numbers popped up constantly, as if its health were being
  recalculated and healed every frame.

Status: reported only. No screenshot, recording or log has been captured yet.
It is not known whether every match does this or only some.

What is known:

- Offline Showdown spawns broken actors: off the 60x60 Skull Creek map, without
  UI objects, or with uninitialised fields. The likely root cause is that the
  offline battle creates fewer player profiles (6) than Showdown players (10).
  See AGENTS.md, "Showdown renderer guards", and the follow-up root-cause
  proposal `showdown-spawn-root`.
- Before the guards, those actors crashed the client. The guards let the match
  continue with them still in it, so their bad state is now visible instead of
  fatal.

Suspected contributors (unproven; test each before changing anything):

1. **Global zero-safe division** (`__aeabi_idiv`/`uidiv`/`idivmod`/`uidivmod`
   PLT wrappers in `scripts/patch_v49_client.py`). A zero divisor now returns
   0. Gameplay or physics code that used to crash may now get 0 for a ratio,
   speed, health fraction or interpolation step. That could plausibly cause
   jumping positions or a heal amount recalculated every frame. The earlier,
   narrower health-divisor guards (`0x242624`, `0x248544`) only affected
   rendering. The global wrapper also reaches game logic.
2. **Off-map / garbage actors** themselves: actors at bogus coordinates (seen
   at tile index 9840 of 3600) being clamped, pushed or teleported by the game
   each frame.
3. **Renderer data-row bounds guard** (`0x249448`): skipping a row for a broken
   actor may leave its visuals (such as the box ring colour) in a default or
   team-specific state. This would explain one blue ring and one red ring.
4. **Missing-profile paths**: actors without a profile take the "no profile"
   or unskinned branches, so their team colour or ring may differ.

Suggested next steps:

1. Record a short video and a screenshot of the chaos on the 9340 build.
2. Build an A/B client identical except **without** the global division
   wrappers (keep the two health-divisor guards). Compare whether flying
   actors and heal spam disappear, and whether SIGFPE crashes return.
3. If the wrappers are responsible, narrow them to rendering call sites only,
   or find the exact logic division and fix its divisor at the source.
4. Fix the spawn/profile root cause so broken actors are never created. That
   should remove all of these symptoms together.
5. Any client change must be published as the public `v49.194` release asset
   after live verification (AGENTS.md, "Publishing Android client updates").

### 2. Other known gaps (carried over from AGENTS.md)

- Upgrade tutorial: "Let's learn to upgrade Brawlers" shows on Home because of
  the real shared power-point balance.
- Individual flying trophy sprites on the Battle End screen are not implemented.
- Gold mastery cosmetic presentation is unverified, and the 6,000-point daily
  mastery cap is not implemented.
- Non-credit Brawl Pass reward types are incomplete.
- Android ID login fallback: the tablet never presents the stored account
  token, so any client sending another device's Android ID can load that
  account (AGENTS.md, 2026-10-18 static audit).
- Battle results are client-reported. The 30-second replay guard limits
  farming but does not prove a match happened.
- Brawl Ball is not playable (see AGENTS.md before attempting it).

## Fixed

(Move entries here with the build SHA-256, date and live evidence once verified.)
