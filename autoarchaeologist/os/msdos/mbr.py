#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   (PC) Master Boot Records
   ========================

'''

from ...base import namespace
from ...base import octetview as ov

MBR_TYPES = {
    0x00: "unused",
    0x01: "Primary DOS with 12 bit FAT",
    0x02: "XENIX / file system",
    0x03: "XENIX /usr file system",
    0x04: "Primary DOS with 16 bit FAT (< 32MB)",
    0x05: "Extended DOS",
    0x06: "Primary DOS, 16 bit FAT (>= 32MB)",
    0x07: "NTFS, OS/2 HPFS, QNX-2 (16 bit) or Advanced UNIX",
    0x08: "AIX file system or SplitDrive",
    0x09: "AIX boot or Coherent",
    0x0A: "OS/2 Boot Manager, OPUS or Coherent swap",
    0x0B: "DOS or Windows 95 with 32 bit FAT",
    0x0C: "DOS or Windows 95 with 32 bit FAT (LBA)",
    0x0E: "Primary 'big' DOS (>= 32MB, LBA)",
    0x0F: "Extended DOS (LBA)",
    0x10: "OPUS",
    0x11: "OS/2 BM: hidden DOS with 12-bit FAT",
    0x12: "Compaq diagnostics",
    0x14: "OS/2 BM: hidden DOS with 16-bit FAT (< 32MB)",
    0x16: "OS/2 BM: hidden DOS with 16-bit FAT (>= 32MB)",
    0x17: "OS/2 BM: hidden IFS (e.g. HPFS)",
    0x18: "AST Windows swapfile",
    0x1b: "ASUS Recovery (NTFS)",
    0x24: "NEC DOS",
    0x3C: "PartitionMagic recovery",
    0x39: "plan9",
    0x40: "VENIX 286",
    0x41: "Linux/MINIX (sharing disk with DRDOS)",
    0x42: "SFS or Linux swap (sharing disk with DRDOS)",
    0x43: "Linux native (sharing disk with DRDOS)",
    0x4D: "QNX 4.2 Primary",
    0x4E: "QNX 4.2 Secondary",
    0x4F: "QNX 4.2 Tertiary",
    0x50: "DM (disk manager)",
    0x51: "DM6 Aux1 (or Novell)",
    0x52: "CP/M or Microport SysV/AT",
    0x53: "DM6 Aux3",
    0x54: "DM6",
    0x55: "EZ-Drive (disk manager)",
    0x56: "Golden Bow (disk manager)",
    0x5c: "Priam Edisk (disk manager)",
    0x61: "SpeedStor",
    0x63: "System V/386 (such as ISC UNIX), GNU HURD or Mach",
    0x64: "Novell Netware/286 2.xx",
    0x65: "Novell Netware/386 3.xx",
    0x6C: "DragonFlyBSD",
    0x70: "DiskSecure Multi-Boot",
    0x75: "PCIX",
    0x77: "QNX4.x",
    0x78: "QNX4.x 2nd part",
    0x79: "QNX4.x 3rd part",
    0x80: "Minix until 1.4a",
    0x81: "Minix since 1.4b, early Linux or Mitac disk manager",
    0x82: "Linux swap or Solaris x86",
    0x83: "Linux native",
    0x84: "OS/2 hidden C: drive",
    0x85: "Linux extended",
    0x86: "NTFS volume set??",
    0x87: "NTFS volume set??",
    0x93: "Amoeba file system",
    0x94: "Amoeba bad block table",
    0x9F: "BSD/OS",
    0xA0: "Suspend to Disk",
    0xA5: "FreeBSD/NetBSD/386BSD",
    0xA6: "OpenBSD",
    0xA7: "NeXTSTEP",
    0xA9: "NetBSD",
    0xAC: "IBM JFS",
    0xAF: "HFS+",
    0xB7: "BSDI BSD/386 file system",
    0xB8: "BSDI BSD/386 swap",
    0xBE: "Solaris x86 boot",
    0xBF: "Solaris x86 (new)",
    0xC1: "DRDOS/sec with 12-bit FAT",
    0xC4: "DRDOS/sec with 16-bit FAT (< 32MB)",
    0xC6: "DRDOS/sec with 16-bit FAT (>= 32MB)",
    0xC7: "Syrinx",
    0xDB: "CP/M, Concurrent CP/M, Concurrent DOS or CTOS",
    0xDE: "DELL Utilities - FAT filesystem",
    0xE1: "DOS access or SpeedStor with 12-bit FAT extended",
    0xE3: "DOS R/O or SpeedStor",
    0xE4: "SpeedStor with 16-bit FAT extended < 1024 cyl.",
    0xEB: "BeOS file system",
    0xEE: "EFI GPT",
    0xEF: "EFI System",
    0xF1: "SpeedStor",
    0xF2: "DOS 3.3+ Secondary",
    0xF4: "SpeedStor large",
    0xFB: "VMware VMFS",
    0xFC: "VMware vmkDiagnostic",
    0xFD: "Linux RAID",
    0xFE: "SpeedStor >1024 cyl. or LANstep",
    0xFF: "Xenix bad blocks table",
}

class NameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "type"),
        ("l", "type"),
        ("r", "start chs"),
        ("r", "stop chs"),
        ("r", "start lba"),
        ("r", "stop lba"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        part = self.ns_priv
        return [
            part.type.val,
            MBR_TYPES.get(part.type.val, "unknown"),
            part.chs_first,
            part.chs_last,
            part.lba_first.val,
            part.lba_last.val,
        ] + super().ns_render()

class BootCode(ov.Dump):
    ''' ... '''

class CHS(ov.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            o1_=ov.Octet,
            o2_=ov.Octet,
            o3_=ov.Octet,
        )
        self.h = self.o1.val
        self.s = self.o2.val & 0x3f
        self.c = self.o3.val | ((self.o2.val << 2) & 0x300)

    def render(self):
        yield "(%d/%d/%d)" % (self.c, self.h, self.s)

class Partition(ov.Struct):
    ''' ... '''
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            status_=ov.Octet,
            chs_first_=CHS,
            type_=ov.Octet,
            chs_last_=CHS,
            lba_first_=ov.Le32,
            lba_last_=ov.Le32,
    )

class Mbr(ov.OctetView):
    ''' ... '''

    def __init__(self, this):

        if this.top not in this.parents:
            return
        if len(this) < 2<<20 or this[0x1fe] != 0x55 or this[0x1ff] != 0xaa:
            return
        super().__init__(this)
        print(this, "MBR")

        # Blank out the rest of the disk (until we implement "extended" partitions)
        ov.Opaque(self, 512, len(this)).insert()

        BootCode(self, 0, 0x1be).insert()
        self.partitions = ov.Array(4, Partition, vertical=True)(self, 0x1be).insert()
        ov.Le16(self, 0x1fe).insert()

        ns = NameSpace(name="", root=this, separator="")

        for n, part in enumerate(self.partitions):
            print(n, part)
            if part.type.val and part.lba_last.val > part.lba_first.val:
                that = this.create(start = part.lba_first.val<<9, stop=part.lba_last.val<<9)
                that.add_type("MBR partition")
            else:
                that = None
            NameSpace(name="%d" % (1+n), parent=ns, priv=part, this=that)

        this.add_interpretation(self, ns.ns_html_plain)
        self.add_interpretation(more=False)
