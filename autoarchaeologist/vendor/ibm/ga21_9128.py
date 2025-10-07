#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Floppies according to GA21-9182
   ===============================
'''

from ...base import octetview as ov
from ...base import namespace
from ...generic import disk

class VolSetNS(namespace.NameSpace):
    ''' ... '''

    TABLE = (
        ("l", "name"),
        ("l", "artifact"),
    )

    def ns_render(self):
        vol, ds = self.ns_priv
        return [
        ] + super().ns_render()

class DataSetNS(namespace.NameSpace):
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
        #("l", "offset_to_next_record_space"),
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
            #hdr.offset_to_next_record_space.txt,
            #hdr.res63.txt,
            hdr.expiration_date.txt,
            #hdr.verify_copy_indicator.txt,
            #hdr.data_set_organization.txt,
            #hdr.res80.txt,
            #hdr.pad81.txt,
        ] + super().ns_render()


class DataSet():
    ''' ... '''

    def __init__(self, ds):
        self.ds = ds
        self.ident = ds.user_name.txt
        self.parts = {}
        self.last = "99"
        self.ns = None

    def __lt__(self, other):
        return self.ident < other.ident

    def add_component(self, vol, data_set, recs):
        seq = data_set.volume_sequence_number.txt
        ind = data_set.multi_volume_indicator.txt
        assert seq not in self.parts
        self.parts[seq] = recs
        if ind == "L":
            self.last = seq
        elif ind == " ":
            self.last = "01"
        else:
            assert ind == "C"

        if len(self.parts) != int(self.last):
            return

        recs = []
        for x, y in sorted(self.parts.items()):
            recs += y
        that = data_set.tree.this.create(records=recs)
        self.ns.ns_set_this(that)
        that.add_name(self.ident.strip())
        that.ga21_9128 = self.ds
        print("DS complete", self.ident, list(self.parts), self.last, that, self.ident)

class VolSet():
    ''' ... '''

    def __init__(self, top, name):
        self.top = top
        self.name = name
        self.volumes = {}
        self.data_sets = {}
        self.vol_namespace = VolSetNS(name='', root=top)
        self.ds_namespace = DataSetNS(name='', root=top)
        top.add_interpretation(self, self.html_interpretation)

    def add_component(self, vol, data_set, recs):
        if vol.tree.this not in self.volumes:
            self.volumes[vol.tree.this] = vol
            VolSetNS(
                name = vol.volname,
                parent = self.vol_namespace,
                priv = (vol, data_set,),
                this = vol.tree.this,
            )

        dsid = data_set.user_name.txt
        ds = self.data_sets.get(dsid)
        if ds is None:
            ds = DataSet(data_set)
            self.data_sets[dsid] = ds
            ds.ns = DataSetNS(
                name = data_set.user_name.txt.strip(),
                parent = self.ds_namespace,
                priv = data_set,
            )

        ds.add_component(vol, data_set, recs)

    def html_interpretation(self, file, this):
        file.write('<h3>IBM GA21-9182 Floppy Multi Volume Set »' + self.name + '«</h3>\n')
        file.write('<h4>Data Sets</h4>\n')
        self.ds_namespace.ns_html_plain_noheader(file, this)
        file.write('<h4>Volumes</h4>\n')
        self.vol_namespace.ns_html_plain_noheader(file, this)

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
        self.volid = self.volume_identifier.txt.strip()
        self.volid += "("
        self.volid += self.owner_identifier.txt.strip()
        self.volname = self.volid + ")"
        while self.volid[-1].isdigit():
            self.volid = self.volid[:-1]
        self.volid += ")"

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
        if this.type_case.decode(volsec.frag[:4]) != "VOL1":
            return

        super().__init__(
            this,
            [],
        )
        self.volhead = Vol1Sector(self, volsec.lo, vertical=True)

        volid = self.volhead.volid
        print(this, "Ga21_9182", "VOLID", volid)
        this.add_name(volid)

        this.add_note("GA21-9182", volid, volhead=self.volhead)

        data_sets = []

        multivol = False
        for sec in range(8, 27):
            hdrsec = this.get_rec((0, 0, sec))
            if this.type_case.decode(hdrsec.frag[:4]) != "HDR1":
                break
            ds = Hdr1Sector(self, hdrsec.lo, vertical=True)
            data_sets.append(ds)
            if ds.multi_volume_indicator.txt != ' ':
                multivol = True

        for data_set in data_sets:
            recs = self.commit_data_set(data_set)
            if not recs:
                print("NOREC", data_set)
                continue
            if not multivol:
                y = this.create(records=recs)
                y.add_name(data_set.user_name.txt.strip())
                y.ga21_9128 = data_set
            else:
                volset_dict = this.top.get_by_class_dict(self)
                volset = volset_dict.get(volid)
                if volset is None:
                    volset = VolSet(this.top, volid)
                    volset_dict[volid] = volset
                volset.add_component(self.volhead, data_set, recs)

        if not multivol:
            self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(more=False)

    def commit_data_set(self, data_set):
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
        return list(x.frag for x in recs)
