#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

''' HH Electronic Comet32 disk partitioning '''

from ...base import octetview as ov
from ...base import namespace

class Partition(ov.Struct):
    '''
	struct partition {
		int pa_size;		/* number of sectors in partition */
		int pa_offset;		/* starting sector number of partition */
	};

    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            size_=ov.Le32,
            offset_=ov.Le32,
        )


class DTab(ov.Struct):
    '''
	typedef struct partition wddata[8];
	/*
	 *  The configuration data stored at sector 10 of the disk.
	 */
	
	struct disktab {
		int dt_magic;		/* the magic number */
		wddata dt_dd;		/* partition data */
		char dt_name[16];	/* a buffer for the name of the disk */
	};
    '''

    def __init__(self, tree, lo):
        super().__init__(
            tree,
            lo,
            magic_=ov.Text(4),
            parts_=ov.Array(8, Partition, vertical=True),
            name_=ov.Text(16),
            vertical=True,
        )
        assert self.magic.txt == "dtab"

class Comet32(ov.OctetView):
    '''
	Comet 32 disk partitioning
    '''

    def __init__(self, this):
        if this.top not in this.parents:
            return
        for a, b in zip(this[0x1400:1404], b'part'):
            if a != b:
                return
        super().__init__(this)
        this.add_note("Comet32")

        ns = namespace.NameSpace(name='', root=this)
        dt = DTab(self, 0x1400).insert()
        for n, part in enumerate(dt.parts):
            tns = namespace.NameSpace(
                name = '%c' % (0x61+n),
                parent = ns,
            )
            if part.size.val == 0:
                continue
            if n == 2:
                continue
            y = ov.This(self, part.offset.val << 9, part.size.val << 9).insert()
            tns.ns_set_this(y.that)

        this.add_interpretation(self, ns.ns_html_plain)
        this.add_interpretation(self, this.html_interpretation_children)
        self.add_interpretation(title="Comet32 HexDump", more=False)
