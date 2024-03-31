#!/usr/bin/env python3

'''
   Floppies according to GA21-9182
   ===============================
'''


from ..base import artifact
from ..base import octetview as ov
from ..base import namespace
from ..generic import disk

C_VOL1 = "VOL1".encode('cp037')
C_HDR1 = "HDR1".encode('cp037')

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

    def start_chs(self):
        return (
            int(self.begining_of_extent.txt[:2]),
            int(self.begining_of_extent.txt[3:4]),
            int(self.begining_of_extent.txt[4:]),
        )

    def end_chs(self):
        return (
            int(self.end_of_data.txt[:2]),
            int(self.end_of_data.txt[3:4]),
            int(self.end_of_data.txt[4:]),
        )

class Ga21_9182(disk.Disk):

    def __init__(self, this):
        if not this.top in this.parents:
            return
        volsec = this.get_rec((0,0,7))
        if volsec.frag[:len(C_VOL1)] != C_VOL1:
            return

        print(this, "Ga21_9182")

        super().__init__(
            this,
            [],
        )
        self.volhead = Vol1Sector(self, volsec.lo, vertical=True)

        self.data_sets = []

        for sec in range(8, 27):
            hdrsec = this.get_rec((0, 0, sec))
            if hdrsec.frag[:len(C_HDR1)] != C_HDR1:
                break
            y = Hdr1Sector(self, hdrsec.lo, vertical=True)
            self.data_sets.append(y)

        for data_set in self.data_sets:
            self.commit_data_set(data_set)

        #this.add_interpretation(self, self.disk_picture)
        self.this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(more=False)

    def commit_data_set(self, data_set):
        chunks = []
        start = data_set.start_chs()
        end = data_set.end_chs()
        for rec in self.this.iter_rec():
            if start <= rec.key < end:
                chunks.append(rec.frag)
        that = self.this.create(records=chunks)
        that.add_note(data_set.user_name.txt.rstrip())
        

        
