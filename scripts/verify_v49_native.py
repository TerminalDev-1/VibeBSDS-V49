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
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R8, UC_ARM_REG_R9,
    UC_ARM_REG_FP, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
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
    # Exercise the real branch and deferred badge actions at several rank
    # boundaries. Mock only allocation/queue insertion, inspecting their ABI.
    for new_rank in (2, 7, 25, 35):
        cpu = emulator()
        frame = 0x200F000
        stack = frame - 0x80
        cpu.reg_write(UC_ARM_REG_FP, frame)
        cpu.reg_write(UC_ARM_REG_SP, stack)
        for offset, value in {-0x30: 0x2000100, -0x34: new_rank,
                              -0x38: 0x2000200, -0x3C: 0x2000300}.items():
            cpu.mem_write(frame + offset, struct.pack("<I", value))
        cpu.mem_write(0x2000200, struct.pack("<I", 1))
        cpu.mem_write(stack + 0x20, struct.pack("<I", 0xDE5CEC))
        cpu.reg_write(UC_ARM_REG_R4, 0x2000400)
        cpu.reg_write(UC_ARM_REG_R7, 0x2000500)
        actions = []
        allocation = [0x2010000]

        def queue_badges(cpu, address, size, user):
            if address == 0xDCBE50:
                assert cpu.reg_read(UC_ARM_REG_R0) == 20
                cpu.reg_write(UC_ARM_REG_R0, allocation[0])
                allocation[0] += 32
                cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            elif address == 0x58F6B8:
                assert cpu.reg_read(UC_ARM_REG_R0) == 0x2000100
                actions.append(struct.unpack("<5I", bytes(cpu.mem_read(
                    cpu.reg_read(UC_ARM_REG_R1), 20))))
                cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, queue_badges)
        cpu.emu_start(0x49C570, 0x49C630, count=100)
        assert cpu.reg_read(UC_ARM_REG_PC) == 0x49C630
        assert actions == [(0xDE5CEC, 0x2000300, 1, 0x2000400, new_rank - 1),
                           (0xDE5CEC, 0x2000300, 1, 0x2000500, new_rank)]
        for register, value in ((UC_ARM_REG_R4, 0x2000400),
                                (UC_ARM_REG_R5, 0x2000200),
                                (UC_ARM_REG_R6, new_rank),
                                (UC_ARM_REG_R7, 0x2000500),
                                (UC_ARM_REG_R8, 0x2000100)):
            assert cpu.reg_read(register) == value
    for index,count,target in [(0,6,0x61a2d4),(5,6,0x61a2d4),(6,6,0x61a844),(9,6,0x61a844),(0,0,0x61a844)]:
        u=Uc(UC_ARCH_ARM,UC_MODE_ARM)
        u.mem_map(0,0x1000000)
        u.mem_write(0,library)
        u.mem_map(0x2000000,0x20000)
        u.reg_write(UC_ARM_REG_FP,0x2001000)
        u.reg_write(UC_ARM_REG_R0,index)
        u.mem_write(0x200100c,struct.pack('<I',0x2002000))
        u.mem_write(0x2002000,struct.pack('<III',0x2003000,count,count))
        u.mem_write(0x2003000,struct.pack('<6I',*[0x2004000+i*0x100 for i in range(6)]))
        u.emu_start(0x61a2c8,target,count=20)
        assert u.reg_read(UC_ARM_REG_PC)==target
        if index<count: assert u.reg_read(UC_ARM_REG_R5)==0x2004000+index*0x100
        print(index,count,hex(target),'PASS')
    for index,count,present,target in [(0,6,True,0x44eb50),(5,6,True,0x44eb50),(6,6,False,0x44ebe8),(15,6,False,0x44ebe8),(0,6,False,0x44ebe8)]:
        u=Uc(UC_ARCH_ARM,UC_MODE_ARM)
        u.mem_map(0,0x1000000)
        u.mem_write(0,library)
        u.mem_map(0x2000000,0x20000)
        u.reg_write(UC_ARM_REG_R5,0x2002000)
        u.reg_write(UC_ARM_REG_R6,index)
        u.mem_write(0x2002000,struct.pack('<III',0x2003000,count,count))
        if index<count:
            u.mem_write(0x2003000+index*4,struct.pack('<I',0x2004000 if present else 0))
            u.mem_write(0x20040e0,struct.pack('<I',0x2005000))
        u.emu_start(0x44eb44,target,count=20)
        assert u.reg_read(UC_ARM_REG_PC)==target
        if present:assert u.reg_read(UC_ARM_REG_R0)==0x2005000
        print('UI',index,count,present,hex(target),'PASS')
    for present in (False, True):
        cpu = emulator()
        profile = 0x2001000 if present else 0
        cpu.reg_write(UC_ARM_REG_R0, profile)
        cpu.mem_write(0x20010EC, struct.pack("<I", 0x2002000))
        target = 0x241F90 if present else 0x241FE8
        cpu.emu_start(0x241F8C, target, count=20)
        assert cpu.reg_read(UC_ARM_REG_PC) == target
        assert cpu.reg_read(UC_ARM_REG_R0) == (0x2002000 if present else 0)
    for hook in (0x242624, 0x248544):
        for numerator, maximum in ((0, 0), (0, 3800), (19000, 3800), (38000, 3800)):
            cpu = emulator()
            cpu.reg_write(UC_ARM_REG_R0, numerator)
            cpu.reg_write(UC_ARM_REG_R1, maximum)
            cpu.reg_write(UC_ARM_REG_R4, 10)
            calls = []

            def divide(cpu, address, size, user):
                if address == 0xDCC020:
                    divisor = cpu.reg_read(UC_ARM_REG_R1)
                    assert divisor > 0
                    calls.append(divisor)
                    cpu.reg_write(UC_ARM_REG_R0, cpu.reg_read(UC_ARM_REG_R0) // divisor)
                    cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

            cpu.hook_add(UC_HOOK_CODE, divide)
            cpu.emu_start(hook, hook + 4, count=20)
            assert cpu.reg_read(UC_ARM_REG_PC) == hook + 4
            assert cpu.reg_read(UC_ARM_REG_R0) == (numerator // maximum if maximum else 0)
            assert calls == ([maximum] if maximum else [])
            assert cpu.reg_read(UC_ARM_REG_R4) == 10
    for index, count, present in ((-1, 6, False), (0, 6, True),
                                  (5, 6, True), (6, 6, False),
                                  (15, 6, False), (0, 6, False)):
        cpu = emulator()
        cpu.reg_write(UC_ARM_REG_R0, index & 0xFFFFFFFF)
        cpu.reg_write(UC_ARM_REG_R6, 0x2002000)
        cpu.reg_write(UC_ARM_REG_R9, 0)
        cpu.mem_write(0x2002000, struct.pack("<III", 0x2003000, count, count))
        if 0 <= index < count:
            cpu.mem_write(0x2003000 + index * 4,
                          struct.pack("<I", 0x2004000 if present else 0))
            cpu.mem_write(0x20040E0, struct.pack("<I", 0x2005000))
        cpu.emu_start(0x450248, 0x450258, count=30)
        assert cpu.reg_read(UC_ARM_REG_PC) == 0x450258
        assert cpu.reg_read(UC_ARM_REG_R9) == (0x2005000 if present else 0)
    for old_flag in (0, 1):
        cpu = emulator()
        cpu.reg_write(UC_ARM_REG_R4, 0x2000000)
        cpu.mem_write(0x20003B4, bytes([old_flag]))
        cpu.emu_start(0x431364, 0x43136C)
        assert cpu.reg_read(UC_ARM_REG_R0) == 0
        assert cpu.mem_read(0x20003B4, 1) == b"\0"
    for remaining in (1, 3, 10):
        cpu = emulator()
        cpu.reg_write(UC_ARM_REG_R0, remaining)
        cpu.emu_start(0x2A34C4, 0x2A34CC)
        assert cpu.reg_read(UC_ARM_REG_PC) == 0x2A34CC
    print("Native ARM checks passed: Bounty, null guards, rank badges, Showdown profiles, health divisor and result transition")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    verify(parser.parse_args().apk)
