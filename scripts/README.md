# V49 Android battle fixes

`patch_v49_client.py` rebuilds an **unsigned** APK from the original compatible
client. It checks the ARM32 `libg.so` SHA-256 before editing it. Keep APKs and
signing files outside Git, and sign with the existing client certificate so
`adb install -r` preserves the `com.projectbsds.v49` installation and its data.

```powershell
python scripts/patch_v49_client.py <original.apk> <unsigned-output.apk> --host <current-LAN-IPv4>
```

Discover the game-server host address at runtime. The script updates the Frida
`redirectHost` configuration and retains its existing port and other options.
It rejects an unsupported library, an occupied code cave, or an in-place file
replacement. Use a compatible original V49.194 APK with the required native
library hash. The patched gameplay release is not accepted as a build input.

The native changes use ARM code in the executable segment's final page of
padding, beginning at `0xdcdeb0`. The segment file/memory sizes grow within that
page; the next segment remains at `0xdce000`.

- `0x6e4448`: guard absent offline-bot rosters during passive lookup; return the
  existing “no passive” sentinel. Profiles with rosters follow the original path.
- `0x61b77c`: guard absent offline-bot rosters during gadget setup.
- `0x652318`: retain the actor and skip a position-dependent special-skill
  callback when its replacement actor is null. This fixes an observed live
  Bounty crash in `0x647878` before the result was submitted.
- `0x2a2f14` and `0x2a2f30`: wrap both arena team-score reads. Variation `3`
  (Bounty) saturates at `20` and sets the existing battle winner field when the
  threshold is reached. The client then uses its normal end controller and
  submits the result. Other variations retain the original score behavior.

This client patch must be paired with the corrected server `23456` result
packet. Its layout was checked against V49 native decoders `0x689944` (message),
`0x696d54` (hero), and `0x687350` (display data). Hero list counts are bytes;
display data includes four VInts; hero statistics end with two shorts, two
fixed integers, and a data reference. Team and MVP flags are separate fields.
The FIRST integer of incoming `14110` is the player-relative outcome (0 win,
1 defeat, 2 draw); its second integer is the local team ID. Outgoing result
and hero-side flags are relative to the local player. Comparing the second
integer with hero.Team incorrectly rewards defeats as victories.

The current offline result request does not include kills, damage, healing,
or an MVP selection. Those result statistics remain empty.

Optional ARM machine-code checks use Unicorn (`pip install unicorn`):

```powershell
python scripts/verify_v49_native.py <patched.apk>
```

These exercise scores below and above 20, both winning teams, other variations,
preservation of an existing winner, and the observed null-roster/null-actor
paths. Real-device verification is still required.

- `0x49c570`: replace eager shared rank-up badge mutation with queued native
  badge actions, so a large trophy award displays each intermediate rank.
  Requires the server's pre-battle score/high-score progression snapshots.
  The ARM verifier checks old/new rank values and preserved registers at
  ranks 2, 7, 25 and 35. Live Brock +750 proof reached rank 25 at 755/800.
  Individual flying trophy sprites are still unfinished.


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
