"""Execute the patched ARM routines with Unicorn (pip install unicorn).

Usage: python scripts/verify_v49_native.py <patched.apk>
This verifies machine-code behavior; live Android matches remain required.
"""
import argparse
from pathlib import Path
import struct
import zipfile

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R8,
)


def verify(apk):
    with zipfile.ZipFile(apk) as archive:
        library = archive.read("lib/armeabi-v7a/libg.so")

    def emulator():
        cpu = Uc(UC_ARCH_ARM, UC_MODE_ARM)
        cpu.mem_map(0, 0x1000000)
        cpu.mem_write(0, library)
        cpu.mem_map(0x2000000, 0x20000)
        cpu.reg_write(UC_ARM_REG_SP, 0x200FFF0)
        cpu.reg_write(UC_ARM_REG_LR, 0x1000)
        return cpu

    cases = [(3, 0, 19, -1, 19, -1), (3, 0, 23, -1, 20, 0),
             (3, 1, 25, -1, 20, 1), (0, 1, 25, -1, 25, -1),
             (3, 1, 22, 0, 20, 0)]
    for mode, team, score, winner, expected_score, expected_winner in cases:
        cpu = emulator()
        battle = 0x2010000
        cpu.reg_write(UC_ARM_REG_R0, battle)
        cpu.reg_write(UC_ARM_REG_R1, team)
        cpu.mem_write(battle + 0xE0, struct.pack("<I", mode))
        cpu.mem_write(battle + 0xD4, struct.pack("<i", winner))

        def score_read(cpu, address, size, user):
            if address == 0x6D1C58:
                cpu.reg_write(UC_ARM_REG_R0, score)
                cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, score_read)
        # Enter through the actual patched call site, exercising its branch,
        # wrapper, register saves, score handling, and return to its caller.
        cpu.reg_write(UC_ARM_REG_LR, 0x1000)
        cpu.emu_start(0x2A2F14, 0x2A2F18, count=100)
        assert cpu.reg_read(UC_ARM_REG_PC) == 0x2A2F18
        assert cpu.reg_read(UC_ARM_REG_R0) == expected_score
        assert struct.unpack("<i", cpu.mem_read(battle + 0xD4, 4))[0] == expected_winner

    cpu = emulator()
    cpu.reg_write(UC_ARM_REG_R0, 0)
    cpu.reg_write(UC_ARM_REG_R8, 0x2011000)
    cpu.emu_start(0x652318, 0x652350, count=10)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x652350
    assert cpu.reg_read(UC_ARM_REG_R8) == 0x2011000

    cpu = emulator()
    cpu.reg_write(UC_ARM_REG_R0, 0x2010000)
    cpu.mem_write(0x201002C, struct.pack("<I", 0))
    cpu.emu_start(0x6E4448, 0x1000, count=10)
    assert cpu.reg_read(UC_ARM_REG_PC) == 0x1000
    assert cpu.reg_read(UC_ARM_REG_R0) == 0xFFFFFFFF
    print("Native ARM checks passed: threshold, mode isolation, winner preservation, null guards")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    verify(parser.parse_args().apk)
