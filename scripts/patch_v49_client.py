"""Build an unsigned V49 APK with offline-battle fixes and a runtime LAN host.

Sign the output with the existing client certificate before installing it.
The native edits are specific to the checked ARM32 V49.194 library.
"""
import argparse
import hashlib
import ipaddress
import json
from pathlib import Path
import struct
import zipfile


LIBRARY_SHA256 = "182ff6ea020262271829c9f43c087b40a13e192900369c0539251985c413602e"
CAVE = 0xDCDEB0


def branch(address, target, link=False):
    displacement = target - address - 8
    if displacement % 4 or not -(1 << 25) <= displacement < (1 << 25):
        raise ValueError("ARM branch target outside range")
    return (0xEB000000 if link else 0xEA000000) | ((displacement // 4) & 0xFFFFFF)


def patch_library(original):
    if hashlib.sha256(original).hexdigest() != LIBRARY_SHA256:
        raise ValueError("Unsupported libg.so: require the original ARM32 V49.194 library")
    data = bytearray(original)
    # Offline bot profiles lack the roster used by passive and gadget lookup.
    # Preserve the original path for profiles which have a roster.
    passive = [0xE590302C, 0xE3530000, 0x03E00000, 0x012FFF1E,
               0xE5900038, branch(CAVE + 20, 0x6E4450)]
    gadget_at = CAVE + 32
    gadget = [0xE3510000, 0x012FFF1E, 0xE591C02C, 0xE35C0000,
              0x012FFF1E, 0xE92D4FF0, 0xE28DB01C,
              branch(gadget_at + 28, 0x61B788)]
    bounty_at = CAVE + 64
    # The two arena score reads share this wrapper. For variation 3 only,
    # saturate the displayed score and set the battle's winner at 20. The
    # existing end controller then sends the normal result to the server.
    bounty = [0xE92D4070, 0xE1A04000, 0xE1A05001,
              branch(bounty_at + 12, 0x6D1C58, True),
              0xE594C0E0, 0xE35C0003, 0x1A000005, 0xE3500014,
              0xBA000003, 0xE3A00014, 0xE594C0D4, 0xE37C0001,
              0x058450D4, 0xE8BD8070]
    skill_at = bounty_at + len(bounty) * 4
    # A special skill path replaces its actor with the return value of
    # 0x636478, which is null in this client. Skip its position-dependent
    # callback when null and retain the original actor for the remaining path.
    skill = [0xE3500000, branch(skill_at + 4, 0x652350) & 0x0FFFFFFF,
             0xE1A08000, branch(skill_at + 12, 0x647878, True),
             branch(skill_at + 16, 0x652320)]
    rank_at = skill_at + len(skill) * 4
    # Rank-up clips share their old/new badge children. Updating all children
    # while building a +750 sequence leaves every clip with the final rank.
    # Queue the existing native rank-badge action for each child immediately
    # before its clip plays, rather than setting its label/skin eagerly.
    rank = [0xE51B8030, 0xE51B6034, 0xE51B5038, 0xE3A00014,
            branch(rank_at + 16, 0xDCBE50, True), 0xE1A01000,
            0xE59D2020, 0xE5812000, 0xE51B203C, 0xE5812004,
            0xE5952000, 0xE5812008, 0xE581400C, 0xE2462001,
            0xE5812010, 0xE1A00008,
            branch(rank_at + 64, 0x58F6B8, True), 0xE3A00014,
            branch(rank_at + 72, 0xDCBE50, True), 0xE1A01000,
            0xE59D2020, 0xE5812000, 0xE51B203C, 0xE5812004,
            0xE5952000, 0xE5812008, 0xE581700C, 0xE5816010,
            0xE1A00008, branch(rank_at + 116, 0x58F6B8, True),
            branch(rank_at + 120, 0x49C630)]
    actor_at = rank_at + len(rank) * 4
    # Neutral Showdown actors (including boxes) can carry an owner index
    # beyond the profile vector. Use the existing missing-profile path.
    actor = [0xE59B100C, 0xE591C008, 0xE150000C,
             (branch(actor_at + 12, 0x61A844) & 0x0FFFFFFF) | 0xA0000000,
             0xE5911000, 0xE7915100, branch(actor_at + 24, 0x61A2D4)]
    ui_at = actor_at + len(actor) * 4
    # The cosmetic renderer has the same unchecked index and can also find
    # a null entry. Its native unskinned fallback preserves neutral actors.
    ui = [0xE5950008, 0xE1560000,
          (branch(ui_at + 8, 0x44EBE8) & 0x0FFFFFFF) | 0xA0000000,
          0xE5950000, 0xE7900106, 0xE3500000,
          branch(ui_at + 24, 0x44EBE8) & 0x0FFFFFFF,
          0xE59000E0, branch(ui_at + 32, 0x44EB50)]
    name_at = CAVE + 24
    name_tail_at = ui_at + len(ui) * 4
    # Actor-name lookup can receive no profile for a neutral actor. Reuse
    # the two padding words after the passive guard and the last two words
    # of this page; skip the caller's name-dependent block when absent.
    name = [0xE3500000, branch(name_at + 4, name_tail_at)]
    name_tail = [branch(name_tail_at, 0x241FE8) & 0x0FFFFFFF,
                 branch(name_tail_at + 4, 0x6E3244)]
    end = name_tail_at + len(name_tail) * 4
    if end > 0xDCE000 or any(data[CAVE:end]):
        raise ValueError("Executable padding is unavailable")
    for address, words in [(CAVE, passive), (gadget_at, gadget),
                           (bounty_at, bounty), (skill_at, skill), (rank_at, rank),
                           (actor_at, actor), (ui_at, ui),
                           (name_at, name), (name_tail_at, name_tail)]:
        struct.pack_into("<" + "I" * len(words), data, address, *words)
    for address, target, link in [(0x6E4448, CAVE, False),
                                  (0x61B77C, gadget_at, False),
                                  (0x2A2F14, bounty_at, True),
                                  (0x2A2F30, bounty_at, True),
                                  (0x652318, skill_at, False),
                                  (0x49C570, rank_at, False),
                                  (0x61A2C8, actor_at, False),
                                  (0x44EB44, ui_at, False),
                                  (0x241F8C, name_at, True)]:
        struct.pack_into("<I", data, address, branch(address, target, link))
    phoff = struct.unpack_from("<I", data, 28)[0]
    stride, count = struct.unpack_from("<HH", data, 42)
    for index in range(count):
        header = phoff + stride * index
        kind, offset, address = struct.unpack_from("<III", data, header)
        if kind == 1 and address == 0x1EC000 and offset == address:
            struct.pack_into("<II", data, header + 16, end - address, end - address)
            break
    else:
        raise ValueError("Expected executable ELF segment was not found")
    # A health-bar frame divides current health by maximum health. Neutral
    # offline actors can have zero maximum health. Render their empty frame
    # instead of calling __aeabi_idiv with a zero divisor (SIGFPE).
    health_at = 0xEB0470
    health = [0xE3510000, 0x03A00000,
              (branch(health_at + 8, 0xDCC020, True) & 0x0FFFFFFF) | 0x10000000,
              branch(health_at + 12, 0x242628)]
    if any(data[health_at:health_at + 16]):
        raise ValueError("Health guard executable padding is unavailable")
    struct.pack_into("<4I", data, health_at, *health)
    struct.pack_into("<I", data, 0x242624, branch(0x242624, health_at))
    for index in range(count):
        header = phoff + stride * index
        if struct.unpack_from("<III", data, header) == (1, 0xEAA000, 0xEAA000):
            struct.pack_into("<II", data, header + 16,
                             health_at + 16 - 0xEAA000, health_at + 16 - 0xEAA000)
            break
    else:
        raise ValueError("Expected secondary executable ELF segment was not found")
    # A second actor UI lookup indexes the profile vector directly. Neutral
    # actors and extra offline bots use the existing no-profile path.
    profile_at = health_at + 16
    profile = [0xE3500000,
               (branch(profile_at + 4, 0x450258) & 0x0FFFFFFF) | 0xB0000000,
               0xE5961004, 0xE1500001,
               (branch(profile_at + 16, 0x450258) & 0x0FFFFFFF) | 0xA0000000,
               0xE5961000, 0xE7910100, 0xE3500000,
               branch(profile_at + 32, 0x450258) & 0x0FFFFFFF,
               0xE59090E0, branch(profile_at + 40, 0x450258)]
    if any(data[profile_at:profile_at + len(profile) * 4]):
        raise ValueError("Actor UI guard executable padding is unavailable")
    struct.pack_into("<11I", data, profile_at, *profile)
    struct.pack_into("<I", data, 0x450248, branch(0x450248, profile_at))
    struct.pack_into("<II", data, header + 16,
                     profile_at + len(profile) * 4 - 0xEAA000,
                     profile_at + len(profile) * 4 - 0xEAA000)
    # The per-frame renderer repeats the same health fraction as setup.
    health_update_at = profile_at + len(profile) * 4
    health_update = [0xE3510000, 0x03A00000,
                     (branch(health_update_at + 8, 0xDCC020, True)
                      & 0x0FFFFFFF) | 0x10000000,
                     branch(health_update_at + 12, 0x248548)]
    if any(data[health_update_at:health_update_at + 16]):
        raise ValueError("Health update guard executable padding is unavailable")
    struct.pack_into("<4I", data, health_update_at, *health_update)
    struct.pack_into("<I", data, 0x248544, branch(0x248544, health_update_at))
    struct.pack_into("<II", data, header + 16,
                     health_update_at + 16 - 0xEAA000,
                     health_update_at + 16 - 0xEAA000)
    # A received result supersedes the practice end state. Keep the handler's
    # zero return, but let the overlay consume the newly stored result once.
    struct.pack_into("<II", data, 0x431364, 0xE3A00000, 0xE5C403B4)
    # This branch is already guarded by a pending result and variation 6.
    # Eliminated Solo players should proceed without waiting for all bots.
    struct.pack_into("<I", data, 0x2A34C8, 0xE320F000)
    return bytes(data)


def build_apk(source, output, host):
    ipaddress.IPv4Address(host)
    if source.resolve() == output.resolve():
        raise ValueError("Output must differ from the original APK")
    with zipfile.ZipFile(source) as archive:
        patched = patch_library(archive.read("lib/armeabi-v7a/libg.so"))
        config_name = "lib/armeabi-v7a/libkagenay.c.so"
        config = json.loads(archive.read(config_name))
        config["interaction"]["parameters"]["redirectHost"] = host
        with zipfile.ZipFile(output, "w") as destination:
            for entry in archive.infolist():
                if entry.filename.startswith("META-INF/") and (
                    entry.filename.endswith((".SF", ".RSA", ".DSA", ".EC"))
                    or entry.filename == "META-INF/MANIFEST.MF"
                ):
                    continue
                payload = archive.read(entry)
                if entry.filename == "lib/armeabi-v7a/libg.so":
                    payload = patched
                elif entry.filename == config_name:
                    payload = json.dumps(config).encode()
                destination.writestr(entry, payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--host", required=True)
    args = parser.parse_args()
    build_apk(args.source, args.output, args.host)
    print(f"Unsigned APK: {args.output}")
