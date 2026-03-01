#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Data General RDOS disks
   =======================

   See: 019-000002-01 S301 RDOS Internal Structures Student Handbook 1977
'''

from ...base import octetview as ov
from ...base import artifact
from ...base import namespace

class RdosNameSpace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("r", "attr"),
        ("r", "last"),
        ("r", "blast"),
        ("r", "lba0"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        udf = self.ns_priv
        return [
            "0x%04x" % udf.attr.val,
            "0x%04x" % udf.last.val,
            "0x%04x" % udf.blast.val,
            "0x%04x" % udf.lbafirst.val,
        ] + super().ns_render()

class PhysDiskInfo(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            revision_=ov.Be16,
            checksum_=ov.Be16,
            tracks_=ov.Be16,
            sectors_=ov.Be16,
            nblock_=ov.Be32,
            framesz_=ov.Be16,
            disktype_=ov.Be16,
            vertical=True,
        )

class RemapInfo(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            nwords_=ov.Be16,
            address_=ov.Be32,
            size_=ov.Be16,
            badblocks_=ov.Array(10, ov.Be32, elide=(0,), vertical=True),
            vertical=True,
        )

class SysDr(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            lba_=ov.Array(255, ov.Be16, vertical=True, elide=(0,)),
            link_=ov.Be16,
            vertical=True,
        )

class Ufd(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            name_=ov.Text(10),
            ext_=ov.Text(2),
            attr_=ov.Be16,
            link_=ov.Be16,
            last_=ov.Be16,
            blast_=ov.Be16,
            lbafirst_=ov.Be16,
            accessed_=ov.Be16,
            created_=ov.Be16,
            tcreated_=ov.Be16,
            udftmp1_=ov.Be16,
            udftmp2_=ov.Be16,
            usecnt_=ov.Be16,
            dctlink_=ov.Be16,
            more=True,
        )
        self.done(-36)
        assert len(self) == 36
        if self[0] == 0:
            self.fname = None
        else:
            self.fname = self.name.txt.strip() + "." + self.ext.txt.strip()

class UfdSector(ov.Struct):
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            count_=ov.Be16,
            dents_=ov.Array(14, Ufd, vertical=True,),
            dummy1_=ov.Be16,
            maxent_=ov.Be16,
            dummy2_=ov.Be16,
            vertical=True,
        )

class RandomFile():
    def __init__(self, tree, udf, ns):
        #print("RND", udf.name, udf.ext, udf.lbafirst, udf.last)
        self.tree = tree
        self.udf = udf
        self.blk = [
            ov.Array(256, ov.Be16)(tree, udf.lbafirst.val << 9).insert()
        ]
        frags = []
        for ilba in range(udf.last.val + 1):
            if ilba > 255:
                break
            ptr = self.blk[0][ilba].val << 9
            y = ov.Opaque(tree, ptr, width=0x200).insert()
            frags.append(y.octets())

        if not frags:
            return

        frags[-1] = frags[-1][:udf.blast.val]
        if len(frags[-1]) == 0:
            frags.pop(-1)
        if not frags:
            return

        that = tree.this.create(records=frags)
        that.add_name(udf.fname)
        ns.ns_set_this(that)

class ContiguousFile():
    def __init__(self, tree, udf, ns):
        #print("CONT", udf.name, udf.ext, udf.lbafirst, udf.last)
        ptr = udf.lbafirst.val << 9
        that = ov.This(tree, ptr, width = (udf.last.val + 1) << 9).insert()
        that.that.add_name(udf.fname)
        ns.ns_set_this(that.that)

class LinkedFile():
    def __init__(self, tree, udf, ns):
        print("LINK", udf.name, udf.ext, udf.lbafirst, udf.last, udf.blast)
        frags = []
        lba = udf.lbafirst.val
        ref = 0x0
        for n in range(udf.last.val + 1):
            ptr = lba << 9
            print("LBA", hex(n), hex(lba), hex(ptr), hex(ref))
            y = ov.Opaque(tree, ptr, width=0x200)
            o = y.octets()
            if len(o) != 512:
                break
            frags.append(o[:510])
            xor = (o[510] << 8) | o[511]
            print(" X", hex(lba), hex(xor), hex(ref ^ xor))
            if xor == 0:
                break
            lban = ref ^ xor
            ref = lba
            lba = lban
        if frags:
            frags[-1] = frags[-1][:udf.blast.val]
            if len(frags[-1]) == 0:
                frags.pop(-1)
            that = tree.this.create(records=frags)
            that.add_name(udf.fname)
            ns.ns_set_this(that)

class RdosDisk(ov.OctetView):
    def __init__(self, this):

        if not this.top in this.parents:
            return

        super().__init__(this)

        print(this, self.__class__.__name__)
        pdi = PhysDiskInfo(self, 3 << 9).insert()
        if pdi.nblock.val not in (
            203 * 2 * 12 - 6,
            77 * 2 * 16 - 6,
        ):
            print(this, "PDI-", pdi)
            return

        this.taken = self
        this.add_note("DG-FS")

        self.ns = RdosNameSpace(
            name="",
            root=this,
        )

        rmi = RemapInfo(self, 4 << 9).insert()
        sysdr = SysDr(self, 6 << 9).insert()
        udfs = []
        for n in sysdr.lba:
            if n.val == 0:
                continue
            y = UfdSector(self, n.val << 9).insert()
            for z in y.dents:
                if this[z.lo] > 0:
                    udfs.append(z)

        for udf in udfs:
            ns = RdosNameSpace(
                name=udf.fname,
                parent=self.ns,
                priv=udf,
            )
            if udf.lbafirst.val == 0:
                continue
            if udf.attr.val & 4 == 4:
                RandomFile(self, udf, ns)
            elif udf.attr.val & 8 == 8:
                ContiguousFile(self, udf, ns)
            else:
                LinkedFile(self, udf, ns)

        this.add_interpretation(self, self.ns.ns_html_plain)
        self.add_interpretation(title="RDOS disk", more=True)
