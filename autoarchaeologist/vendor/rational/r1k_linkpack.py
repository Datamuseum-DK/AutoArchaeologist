#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

# pylint: disable=E1101
'''
   'a2' type 'This is a Link Pack.' segments
'''

from . import r1k_bittools as bittools

class MagicString(bittools.R1kSegBase):
    ''' The magic 'This is a Link Pack.' marker '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, 0x14*8),
            title="MAGIC_STRING",
            **kwargs,
        )
        _i, self.text = bittools.to_text(seg, self.chunk, 0, 0x14)

    def render(self, _chunk, fo):
        ''' one line '''
        fo.write(self.title + ' "' + self.text + '"\n')

class Header(bittools.R1kSegBase):
    ''' Looks like the overall header '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, -1),
            title="HEADER",
            **kwargs,
        )
        #self.compact = True
        self.get_fields(
            ("hdr_f0_n", 32),
            ("hdr_f1_n", 32),
            ("hdr_f2_n", 32),
            ("hdr_f3_n", 32),
            ("hdr_f4_n", 32),
            ("hdr_f5_p", 33),
        )
        self.finish()
        assert self.offset == 0xc1

class Thing1(bittools.R1kSegBase):
    ''' Looks like a Y-branch in a tree, but also used as a list '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, -1),
            title="THING1",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t1_str1_p", 32),
            ("t1_str2_p", 32),
            ("t1_h2", 32),
            ("t1_h3", 32),
            ("t1_h4", 32),
            ("t1_left_p", 32),
            ("t1_right_p", 32),
            ("t1_tail", 1),
        )
        self.finish()
        assert self.offset == 0xe1
        self.str1 = bittools.make_one(self, 't1_str1_p', Thing2B, func=mk_thing2b)
        self.str2 = bittools.make_one(self, 't1_str2_p', Thing2B, func=mk_thing2b)
        self.left = bittools.make_one(self, 't1_left_p', Thing1)
        self.right = bittools.make_one(self, 't1_right_p', Thing1)

    def dump(self, fo):
        ''' Custom summary of the look-up table '''
        fo.write("    ")
        fo.write(" 0x%x" % self.t1_h2)
        fo.write(" 0x%06x" % self.t1_h3)
        fo.write(" 0x%x" % self.t1_h4)
        fo.write(" 0x%x" % self.t1_tail)
        fo.write(" " + self.str1.text.ljust(40))
        fo.write(" " + self.str2.text)
        fo.write("\n")
        if self.left:
            self.left.dump(fo)
        if self.right:
            self.right.dump(fo)

class Thing2A(bittools.R1kSegBase):
    ''' Head of a variant record '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, -1),
            title="THING2A",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t2a_var", 0x1),
            ("t2a_head", 0x33),
        )
        self.finish()

class Thing2B(bittools.R1kSegBase):
    ''' String version of body '''
    def __init__(self, seg, address, **kwargs):
        p = seg.mkcut(address)
        length = int(p[32:64], 2)
        super().__init__(
            seg,
            seg.cut(address, 0x40 + length * 8),
            title="THING2B",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t2b_x", 0x20),
            ("t2b_y", 0x20),
        )
        i, self.text = bittools.to_text(seg, self.chunk, self.offset, self.t2b_y)
        self.offset += 8 * i
        self.finish()

    def render(self, _chunk, fo):
        ''' One line '''
        fo.write(self.title + " ")
        self.render_fields_compact(fo)
        fo.write(' "' + self.text + '"\n')

class Thing2C(bittools.R1kSegBase):
    ''' Pointer version of body '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, -1),
            title="THING2C",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t2c_h0_n", 0x20),
            ("t2c_h1_p", 0x20),
            ("t2c_h2_p", 0x20),
            ("t2c_h3_p", 0x20),
        )
        self.finish()

def mk_thing2x(seg, address, **kwargs):
    ''' Create head+body(+tail) '''
    head = Thing2A(seg, address, **kwargs)
    seg.dot.node(head, 'shape=hexagon')
    if head.t2a_var and (head.t2a_head & 0xffff):
        body = Thing2B(seg, address + 0x34, **kwargs)
        seg.dot.node(body, 'shape=plaintext', 'label="%s"' % body.text)
    else:
        body = Thing2C(seg, address + 0x34, **kwargs)
        seg.dot.node(body, "shape=box")

        if body.t2c_h1_p < seg.end - 2:
            bittools.make_one(body, 't2c_h1_p', Thing2A, func=mk_thing2a)
        bittools.make_one(body, 't2c_h2_p', Thing2A, func=mk_thing2a)
        bittools.make_one(body, 't2c_h3_p', Thing2A, func=mk_thing2a)
    seg.dot.edge(head, body)
    return head, body

def mk_thing2a(seg, address, **kwargs):
    ''' Create and return the head '''
    head, _body = mk_thing2x(seg, address, **kwargs)
    return head

def mk_thing2b(seg, address, **kwargs):
    ''' Create and return the body '''
    _head, body = mk_thing2x(seg, address - 0x34, **kwargs)
    return body

class Thing3(bittools.R1kSegBase):
    ''' no idea '''
    def __init__(self, seg, address, **kwargs):
        super().__init__(
            seg,
            seg.cut(address, -1),
            title="THING3",
            **kwargs,
        )
        self.compact = True
        self.get_fields(
            ("t3_h0", 32),
            ("t3_h1", 32),
            ("t3_t2_p", 32),
            ("t3_h3", 32),
            ("t3_h4", 32),
            ("t3_t1_p", 32),
        )
        self.finish()
        assert self.offset == 0xc0
        bittools.make_one(self, 't3_t2_p', Thing2A, func=mk_thing2a)
        if self.t3_t1_p < seg.end:
            bittools.make_one(self, 't3_t1_p', Thing1)

class R1kSegLinkPack():
    ''' A Link Pack Segment '''
    def __init__(self, seg, chunk):
        #print("?R1KLP", seg.this, chunk)
        seg.this.add_note("R1K_Link_Pack")
        y = MagicString(seg, chunk.begin)
        self.hdr = Header(seg, y.end)
        a = self.hdr.end

        self.tbl5 = bittools.BitPointerArray(
            seg,
            a,
            (self.hdr.hdr_f5_p - a) // 32
        )

        self.root = []
        for n, field in enumerate(self.tbl5):
            if field.val:
                y = Thing1(seg, field.val)
                self.root.append((n, y))
                seg.dot.edge(self.hdr, y)

        bittools.make_one(self.hdr, 'hdr_f5_p', Thing3)

        if False:
            for n, i in self.root:
                i.dump(seg.tfile)
            seg.tfile.write("\n")

