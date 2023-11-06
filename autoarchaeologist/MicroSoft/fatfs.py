#!/usr/bin/env python3

'''
   Microsoft FATFS

'''

#from ..generic import disk
from ..base import type_case
from ..base import namespace
from ..base import octetview as ov

L_SECTOR_LENGTH = 512
L_SECTOR_SHIFT = 9

class MsDosTypeCase(type_case.WellKnown):
    ''' ... '''

    def __init__(self):
        super().__init__("cp850")
        self.set_slug(0x0d, ' ', '')
        self.set_slug(0x10, ' ', '«dle»')
        self.set_slug(0x11, ' ', '«dc1»')
        self.set_slug(0x1a, ' ', '«eof»', self.EOF)

msdostypecase = MsDosTypeCase()


class BiosParamBlock33(ov.Struct):
    ''' ... '''
  
    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            bsBytesPerSec_=ov.Le16,
            bsSectPerClust_=ov.Octet,
            bsResSectors_=ov.Le16,
            bsFATS_=ov.Octet,
            bsRootDirEnts_=ov.Le16,
            bsSectors_=ov.Le16,
            bsMedia_=ov.Octet,
            bsFATsecs_=ov.Le16,
            bsSectPerTrack_=ov.Le16,
            bsHeads_=ov.Le16,
            bsHiddenSecs_=ov.Le16,
        )

    def is_sane(self):
        if self.bsBytesPerSec.val & (self.bsBytesPerSec.val -1):
            return False
        if not self.bsSectPerClust.val:
            return False
        return True

class BootSector33(ov.Struct):
    '''
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            vertical=True,
            jmp_=3,
            oem_=ov.Text(8),
            bpb_=BiosParamBlock33,
            driveno_=ov.Octet,
            bootcode__=479,
            bootsig_=ov.Le16,
        )

    def is_sane(self):
        if self.jmp[0] not in (0xe9, 0xeb):
            return False
        if self.bootsig.val != 0xaa55:
            return False
        return self.bpb.is_sane()

class DirEnt(ov.Struct):
    '''
    '''

    def __init__(self, tree, lo, pns):
        super().__init__(
            tree,
            lo,
            vertical=False,
            name_=ov.Text(11),
            attr_=ov.Octet,
            locase_=ov.Octet,
            ctime_=ov.Le24,
            cdate_=ov.Le16,
            adate_=ov.Le16,
            hicl_=ov.Le16,
            mtime_=ov.Le16,
            mdate_=ov.Le16,
            cluster_=ov.Le16,
            length_=ov.Le32,
        )
        self.deleted = self[0] == 0xe5
        self.unused = self[0] == 0x00
        self.valid = not (self.deleted or self.unused)
        self.subdir = None
        i = self.name.txt[:8].rstrip() + "."
        i += self.name.txt[8:].rstrip()
        if self.valid:
            self.namespace = NameSpace(
                name=i,
                parent=pns,
                separator='\\',
            )
        else:
            self.namespace = None

    def commit(self):
        ''' ... '''
        if not self.valid:
            return
        if self.attr.val in(0x20, 0x27,):
            sz = self.length.val
            if sz == 0:
                return
            j = []
            for _lo, i in self.tree.get_chain(self, self.cluster.val):
                want = min(sz, self.tree.clustersize)
                j.append(i[:want])
                sz -= want
            if j:
                that = self.tree.this.create(records=j)
                self.namespace.ns_set_this(that)
                # print("TT", de.length.val, len(that), that)
        if self.attr.val in(0x10,):
            self.subdir = Directory(self.tree, self.namespace)
            for lo, cluster in self.tree.get_chain(self, self.cluster.val):
                for adr in range(lo, lo + len(cluster), 0x20):
                    j = DirEnt(self.tree, adr, self.namespace).insert()
                    self.subdir.add_dirent(j)
            self.subdir.commit()
          

class FAT12(ov.Octets):
    ''' ... '''

    def __init__(self, tree, lo, width):
        super().__init__(tree, lo, width=width)
        self.clusters = []
        for i in range(0, width, 3):
            j = ((self[i + 1] & 0xf) << 8) | self[i]
            self.clusters.append(j)
            j = (self[i + 1] >> 4) | (self[i + 2] << 4)
            self.clusters.append(j)
        self.owner = [None] * len(self.clusters)

    def chain(self, owner,  first):
        while first < len(self.owner) and self.owner[first] is None:
            yield first
            self.owner[first] = owner
            first = self.clusters[first]
            if first == 0xfff:
                return

    def render(self):
        for i in range(0, len(self.clusters), 16):
            yield ",".join("%03x" % x for x in self.clusters[i:i+16]) + " // [0x%x]" % i

class NameSpace(namespace.NameSpace):
    ''' ... '''

    xTABLE = (
        ("r", "bfd"),
        ("r", "ok"),
        ("r", "-"),
        ("r", "-"),
        ("r", "type"),
        ("r", "length"),
        ("r", "-"),
        ("r", "nsect"),
        ("r", "-"),
        ("r", "areasz"),
        ("r", "sector"),
        ("r", "-"),
        ("r", "-"),
        ("r", "flags"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def xns_render(self):
        sfd = self.ns_priv
        bfd = sfd.bfd
        return [
            sfd.file.val,
            bfd.ok.val,
            bfd.bfd01.val,
            bfd.bfd02.val,
            hex(bfd.type.val),
            bfd.length.val,
            bfd.bfd05.val,
            bfd.nsect.val,
            bfd.bfd07.val,
            bfd.areasz.val,
            bfd.sector.val,
            bfd.bfd0a.val,
            bfd.bfd0b.val,
            hex(bfd.flags.val),
        ] + super().ns_render()

class Directory():
    def __init__(self, tree, namespace):
        self.tree = tree
        self.namespace = namespace
        self.dirents = []

    def add_dirent(self, dirent):
        self.dirents.append(dirent)

    def commit(self):
        for de in self.dirents: 
            de.commit()

class Cluster(ov.Opaque):
    ''' ... '''

    def __init__(self, tree, lo, width, owner):
        super().__init__(tree, lo, width=width)
        self.owner = owner

    def render(self):
        yield "Cluster(%s)" % self.owner.name.txt

class FatFs(ov.OctetView):

    def __init__(self, this):

        if this.top not in this.parents:
            return
        super().__init__(this)

        this.type_case = msdostypecase
        bootsec = BootSector33(self, 0).insert()
        #print("BS", bootsec, bootsec.is_sane())
        if not bootsec.is_sane():
            return
        this.add_note("FatFS")

        print("FatFs", this, self)

        secsize = bootsec.bpb.bsBytesPerSec.val
        self.clustersize = secsize * bootsec.bpb.bsSectPerClust.val
        ncluster = bootsec.bpb.bsSectors.val // bootsec.bpb.bsSectPerClust.val
        fatsize = ncluster + ncluster // 2
        fatsect = (fatsize + secsize - 1) // secsize
        assert bootsec.bpb.bsFATsecs.val == fatsect
        print("NC", secsize, ncluster, fatsize, fatsect)
        dirstart = bootsec.bpb.bsResSectors.val * secsize
        self.fat1 = FAT12(self, dirstart, fatsect * secsize).insert()
        if bootsec.bpb.bsFATS.val == 1:
            self.fat2 = self.fat1
        elif bootsec.bpb.bsFATS.val == 2:
            self.fat2 = FAT12(self, self.fat1.hi, fatsect * secsize).insert()
        else:
            print("NFAT", bootsec.bpb.bsFATS.val)
        
        self.namespace = NameSpace(
            name="",
            root=this,
            separator="",
        )

        root = Directory(self, self.namespace)
        adr = self.fat2.hi
        for i in range(bootsec.bpb.bsRootDirEnts.val):
            j = DirEnt(self, adr, self.namespace).insert()
            adr = j.hi
            root.add_dirent(j)
        self.cluster2 = adr
        print("CSZ", self.clustersize, hex(self.cluster2))

        root.commit()


        this.add_interpretation(self, self.namespace.ns_html_plain)

        self.add_interpretation()

    def get_chain(self, owner, cluster):
        for clno in self.fat1.chain(owner, cluster):
            i = self.cluster2 + (clno-2) * self.clustersize
            Cluster(self, i, self.clustersize, owner).insert()
            yield i, self.this[i:i+self.clustersize]
