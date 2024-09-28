#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Floppies according to GA21-9182
   ===============================
'''

from ...base import artifact
from ...base import octetview as ov
from ...base import namespace
from ...generic import disk

C_VOL1 = "VOL1".encode('cp037')
C_HDR1 = "HDR1".encode('cp037')

class MVNamespace(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        #("l", "res5"),
        ("l", "block_length"),
        ("l", "record_attribute"),
        ("l", "physical_record_length"),
        #("l", "record_block_format"),
        #("l", "bypass_indicator"),
        #("l", "data_set_security"),
        #("l", "write_protect"),
        ("l", "exchange_type_indicator"),
        #("l", "multi_volume_indicator"),
        #("l", "volume_sequence_number"),
        ("l", "creation_date"),
        ("l", "record_length"),
        ("l", "offset_to_next_record_space"),
        #("l", "res63"),
        ("l", "expiration_date"),
        #("l", "verify_copy_indicator"),
        #("l", "data_set_organization"),
        #("l", "res80"),
        #("l", "pad81"),
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        hdr = self.ns_priv
        if hdr is None:
            return [ [] * (len(self.TABLE) - 2) ] + super().ns_render()
        return [
            #hdr.res5.txt,
            hdr.block_length.txt,
            hdr.record_attribute.txt,
            hdr.physical_record_length.txt,
            #hdr.record_block_format.txt,
            #hdr.bypass_indicator.txt,
            #hdr.data_set_security.txt,
            #hdr.write_protect.txt,
            hdr.exchange_type_indicator.txt,
            #hdr.multi_volume_indicator.txt,
            #hdr.volume_sequence_number.txt,
            hdr.creation_date.txt,
            hdr.record_length.txt,
            hdr.offset_to_next_record_space.txt,
            #hdr.res63.txt,
            hdr.expiration_date.txt,
            #hdr.verify_copy_indicator.txt,
            #hdr.data_set_organization.txt,
            #hdr.res80.txt,
            #hdr.pad81.txt,
        ] + super().ns_render()

class MVolFile():
    ''' ... '''

    def __init__(self, volset):
        self.volset = volset
        self.frags = {}
        self.that = None

    def add_frag(self, frag):
        if self.that is not None:
            print("MVF already done", self, frag)
            return
        assert self.that is None
        assert frag.seq not in self.frags
        self.frags[frag.seq.strip()] = frag
        self.process()

    def process(self):
        last = self.frags.get("")
        if last is not None:
            self.commit_file(last, last.recs)
            # print("COMPLETE S", last.user_name.txt)
            return
        last_vol = max(self.frags)
        last = self.frags.get(last_vol)
        if last.multi_volume_indicator.txt != "L":
            return
        if len(self.frags) != int(last_vol):
            return
        #print("COMPLETE M", last.user_name.txt)
        recs = []
        for seq, frag in sorted((int(x.seq), x) for x in self.frags.values()):
            # print("  No", seq, frag.tree.this)
            recs += frag.recs
        self.commit_file(last, recs)

    def commit_file(self, last, recs):
        self.that = last.tree.this.create(records=recs)
        if b'_UNREAD__UNREAD_' in self.that.tobytes():
            self.that.add_note("BADSECT")
        self.that.ga21_9128 = last
        ns = MVNamespace(
            name = last.user_name.txt.strip(),
            parent = self.volset.namespace,
            this = self.that,
            priv = last,
        )

    def dump(self, file):
        for nbr, frag in sorted(self.frags.items()):
            file.write("  " + frag.seq + " " + str(frag) + "\n")

class MultiVol():
    ''' ... '''

    def __init__(self, top, name):
        self.top = top
        self.name = name
        self.volumes = []
        self.files = {}
        self.namespace = MVNamespace(name='', root=top)
        self.namespace.KIND = "IBM S34 Floppy Multi Volume Set »" + name + "«"
        #top.add_interpretation(self, self.namespace.ns_html_plain)
        #top.add_interpretation(self, self.html_interpretation)

    def add_volume(self, vol, this):
        if not self.volumes:
            self.top.add_interpretation(self, self.html_interpretation)
        self.volumes.append((vol, this))

    def add_part(self, that, frag):
        mvolfile = self.files.setdefault(
            frag.user_name.txt,
            MVolFile(self),
        )
        mvolfile.add_frag(frag)

    def html_interpretation(self, file, this):
        self.namespace.ns_html_plain(file, this)
        file.write("<pre>\n")
        file.write("Component Volumes:\n")
        for i, j in self.volumes:
            file.write("  (" + i.owner_identifier.txt.strip() + ")")
            file.write("  " + j.summary() + "\n")
        incomplete = False
        for i, j in sorted(self.files.items()):
            if j.that is None:
                incomplete = True
        if incomplete:
            file.write("Incomplete Data Sets:\n")
            for i, j in sorted(self.files.items()):
                if j.that is not None:
                    continue
                file.write("  " + i + "\n")
                j.dump(file)
        file.write("</pre>\n")

class Vol1Sector(ov.Struct):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            tag_=ov.Text(4),
            volume_identifier_=ov.Text(6),
            volume_accessibility_=ov.Text(1),
            res12_=ov.Text(13),
            system_code_=ov.Text(13),
            owner_identifier_=ov.Text(14),
            res52_=ov.Text(13),
            label_extension_indicator_=ov.Text(1),
            res66_=ov.Text(6),
            volume_surface_indicator_=ov.Text(1),
            extent_arrangement_indicator_=ov.Text(1),
            special_requirements_indicator_=ov.Text(1),
            res75_=ov.Text(1),
            physical_record_length_=ov.Text(1),
            physical_record_sequence_code_=ov.Text(2),
            res79_=ov.Text(1),
            label_version_=ov.Text(1),
            pad81_=ov.Text(48),
            **kwargs,
        )
        self.insert()

class Hdr1Sector(ov.Struct):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            tag_=ov.Text(4),
            res5_=ov.Text(1),
            user_name_=ov.Text(17),
            block_length_=ov.Text(5),
            record_attribute_=ov.Text(1),
            begining_of_extent_=ov.Text(5),
            physical_record_length_=ov.Text(1),
            end_of_extent_=ov.Text(5),
            record_block_format_=ov.Text(1),
            bypass_indicator_=ov.Text(1),
            data_set_security_=ov.Text(1),
            write_protect_=ov.Text(1),
            exchange_type_indicator_=ov.Text(1),
            multi_volume_indicator_=ov.Text(1),
            volume_sequence_number_=ov.Text(2),
            creation_date_=ov.Text(6),
            record_length_=ov.Text(4),
            offset_to_next_record_space_=ov.Text(5),
            res63_=ov.Text(4),
            expiration_date_=ov.Text(6),
            verify_copy_indicator_=ov.Text(1),
            data_set_organization_=ov.Text(1),
            end_of_data_=ov.Text(5),
            res80_=ov.Text(1),
            pad81_=ov.Text(48),
            **kwargs,
        )
        self.insert()
        self.recs = []
        self.seq = self.volume_sequence_number.txt

    def start_chs(self):
        i = self.begining_of_extent.txt
        return (int(i[:2]), int(i[2:3]), int(i[3:]))

    def end_chs(self):
        i = self.end_of_extent.txt
        if i == "":
            i = self.end_of_data.txt.strip()
        return (int(i[:2]), int(i[2:3]), int(i[3:]))

class Ga21_9182(disk.Disk):

    def __init__(self, this):
        if not this.top in this.parents:
            return
        try:
            volsec = this.get_rec((0,0,7))
        except KeyError:
            return
        if volsec.frag[:len(C_VOL1)] != C_VOL1:
            return

        print(this, "Ga21_9182")

        super().__init__(
            this,
            [],
        )
        self.volhead = Vol1Sector(self, volsec.lo, vertical=True)

        volid = self.volhead.volume_identifier.txt.strip()
        volid += "("
        volid += self.volhead.owner_identifier.txt.strip()
        while volid[-1].isdigit():
            volid = volid[:-1]
        volid += ")"
        print(this, "VOLID", volid)

        multivol = this.top.multivol.get(volid)
        if multivol is None:
            multivol = MultiVol(this.top, volid)
            this.top.multivol[volid] = multivol

        multivol.add_volume(self.volhead, this)

        self.data_sets = []

        for sec in range(8, 27):
            hdrsec = this.get_rec((0, 0, sec))
            if hdrsec.frag[:len(C_HDR1)] != C_HDR1:
                break
            y = Hdr1Sector(self, hdrsec.lo, vertical=True)
            self.data_sets.append(y)

        for data_set in self.data_sets:
            self.commit_data_set(data_set, multivol)

        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(more=False)

    def commit_data_set(self, data_set, multivol):
        start = data_set.start_chs()
        end = data_set.end_chs()
        recs = []
        for rec in self.this.iter_rec():
            if start <= rec.key <= end:
                recs.append(rec)
                data_set.recs.append(rec.frag)
        if len(recs) == 0:
            print(self.this, "DS", data_set.user_name.txt, "No Records")
            return
        y = ov.Opaque(
            self,
            lo=recs[0].lo,
            hi=recs[-1].hi,
            rendered="Segment " + data_set.user_name.txt,
        )
        y.insert()
        multivol.add_part(self.this, data_set)
