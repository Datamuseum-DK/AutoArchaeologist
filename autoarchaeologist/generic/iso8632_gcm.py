#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    ISO 8632-3 Computer Graphics Metafiles
    --------------------------------------

    A very rudimentary SVG renderer for possibly flawed CGM files


'''

import math
import struct
import html

class CGM_Trouble(Exception):
    ''' Murphy Field Calibration Activated '''

ISO8632_3 = {
    (0, 0): ("no-op", ),
    (0, 1): ("BEGIN METAFILE", ),
    (0, 2): ("END METAFILE", ),
    (0, 3): ("BEGIN PICTURE", ),
    (0, 4): ("BEGIN PICTURE BODY", ),
    (0, 5): ("END PICTURE", ),
    (0, 6): ("BEGIN SEGMENT", ),
    (0, 7): ("END SEGMENT", ),
    (0, 8): ("BEGIN FIGURE", ),
    (0, 9): ("END FIGURE", ),
    (0, 13): ("BEGIN PROTECTION REGION", ),
    (0, 14): ("END PROTECTION REGION", ),
    (0, 15): ("BEGIN COMPOUND LINE", ),
    (0, 16): ("END COMPOUND LINE", ),
    (0, 17): ("BEGIN COMPOUND TEXT PATH", ),
    (0, 18): ("END COMPOUND TEXT PATH", ),
    (0, 19): ("BEGIN TILE ARRAY", ),
    (0, 20): ("END TILE ARRAY", ),
    (0, 21): ("BEGIN APPLICATION STRUCTURE", ),
    (0, 22): ("BEGIN APPLICATION STRUCTURE BODY", ),
    (0, 23): ("END APPLICATION STRUCTURE", ),

    (1, 1): ("METAFILE VERSION", ),
    (1, 2): ("METAFILE DESCRIPTION", ),
    (1, 3): ("VDC TYPE", ),
    (1, 4): ("INTEGER PRECISION", ),
    (1, 5): ("REAL PRECISION", ),
    (1, 6): ("INDEX PRECISION", ),
    (1, 7): ("COLOUR PRECISION", ),
    (1, 8): ("COLOUR INDEX PRECISION", ),
    (1, 9): ("MAXIMUM COLOUR INDEX", ),
    (1, 10): ("COLOUR VALUE EXTENT", ),
    (1, 11): ("METAFILE ELEMENT LIST", ),
    (1, 12): ("METAFILE DEFAULTS REPLACEMENT", ),
    (1, 13): ("FONT LIST", ),
    (1, 14): ("CHARACTER SET LIST", ),
    (1, 15): ("CHARACTER CODING ANNOUNCER", ),
    (1, 16): ("NAME PRECISION", ),
    (1, 17): ("MAXIMUM VDC EXTENT", ),
    (1, 18): ("SEGMENT PRIORITY EXTENT", ),
    (1, 19): ("COLOUR MODEL", ),
    (1, 20): ("COLOUR CALIBRATION", ),
    (1, 21): ("FONT PROPERTIES", ),
    (1, 22): ("GLYPH MAPPING", ),
    (1, 23): ("SYMBOL LIBRARY LIST", ),
    (1, 24): ("PICTURE DIRECTORY", ),

    (2, 1): ("SCALING MODE", ),
    (2, 2): ("COLOUR SELECTION MODE", ),
    (2, 3): ("LINE WIDTH SPECIFICATION MODE", ),
    (2, 4): ("MARKER SIZE SPECIFICATION MODE", ),
    (2, 5): ("EDGE WIDTH SPECIFICATION MODE", ),
    (2, 6): ("VDC EXTENT", ),
    (2, 7): ("BACKGROUND COLOUR", ),
    (2, 8): ("DEVICE VIEWPORT", ),
    (2, 9): ("DEVICE VIEWPORT SPECIFICATION MODE", ),
    (2, 10): ("DEVICE VIEWPORT MAPPING", ),
    (2, 11): ("LINE REPRESENTATION", ),
    (2, 12): ("MARKER REPRESENTATION", ),
    (2, 13): ("TEXT REPRESENTATION", ),
    (2, 14): ("FILL REPRESENTATION", ),
    (2, 15): ("EDGE REPRESENTATION", ),
    (2, 16): ("INTERIOR STYLE SPECIFICATION MODE", ),
    (2, 17): ("LINE AND EDGE TYPE DEFINITION", ),
    (2, 18): ("HATCH STYLE DEFINITION", ),
    (2, 19): ("GEOMETRIC PATTERN DEFINITION", ),
    (2, 20): ("APPLICATION STRUCTURE DIRECTORY", ),

    (3, 1): ("VDC INTEGER PRECISION", ),
    (3, 2): ("VDC REAL PRECISION", ),
    (3, 3): ("AUXILIARY COLOUR", ),
    (3, 4): ("TRANSPARENCY", ),
    (3, 5): ("CLIP RECTANGLE", ),
    (3, 6): ("CLIP INDICATOR", ),
    (3, 7): ("LINE CLIPPING MODE", ),
    (3, 8): ("MARKER CLIPPING MODE", ),
    (3, 9): ("EDGE CLIPPING MODE", ),
    (3, 10): ("NEW REGION", ),
    (3, 11): ("SAVE PRIMITIVE CONTEXT", ),
    (3, 12): ("RESTORE PRIMITIVE CONTEXT", ),
    (3, 17): ("PROTECTION REGION INDICATOR", ),
    (3, 18): ("GENERALIZED TEXT PATH MODE", ),
    (3, 19): ("MITRE LIMIT", ),
    (3, 20): ("TRANSPARENT CELL COLOUR", ),

    (4, 1): ("POLYLINE", ),
    (4, 2): ("DISJOINT POLYLINE", ),
    (4, 3): ("POLYMARKER", ),
    (4, 4): ("TEXT", ),
    (4, 5): ("RESTRICTED TEXT", ),
    (4, 6): ("APPEND TEXT", ),
    (4, 7): ("POLYGON", ),
    (4, 8): ("POLYGON SET", ),
    (4, 9): ("CELL ARRAY", ),
    (4, 10): ("GENERALIZED DRAWING PRIMITIVE", ),
    (4, 11): ("RECTANGLE", ),
    (4, 12): ("CIRCLE", ),
    (4, 13): ("CIRCULAR ARC 3 POINT", ),
    (4, 14): ("CIRCULAR ARC 3 POINT CLOSE", ),
    (4, 15): ("CIRCULAR ARC CENTRE", ),
    (4, 16): ("CIRCULAR ARC CENTRE CLOSE", ),
    (4, 17): ("ELLIPSE", ),
    (4, 18): ("ELLIPTICAL ARC", ),
    (4, 19): ("ELLIPTICAL ARC CLOSE", ),
    (4, 20): ("CIRCULAR ARC CENTRE REVERSED", ),
    (4, 21): ("CONNECTING EDGE", ),
    (4, 22): ("HYPERBOLIC ARC", ),
    (4, 23): ("PARABOLIC ARC", ),
    (4, 24): ("NON-UNIFORM B-SPLINE", ),
    (4, 25): ("NON-UNIFORM RATIONAL B-SPLINE", ),
    (4, 26): ("POLYBEZIER", ),
    (4, 27): ("POLYSYMBOL", ),
    (4, 28): ("BITONAL TILE", ),
    (4, 29): ("TILE", ),

    (5, 1): ("LINE BUNDLE INDEX", ),
    (5, 2): ("LINE TYPE", ),
    (5, 3): ("LINE WIDTH", ),
    (5, 4): ("LINE COLOUR", ),
    (5, 5): ("MARKER BUNDLE INDEX", ),
    (5, 6): ("MARKER TYPE", ),
    (5, 7): ("MARKER SIZE", ),
    (5, 8): ("MARKER COLOUR", ),
    (5, 9): ("TEXT BUNDLE INDEX", ),
    (5, 10): ("TEXT FONT INDEX", ),
    (5, 11): ("TEXT PRECISION", ),
    (5, 12): ("CHARACTER EXPANSION FACTOR", ),
    (5, 13): ("CHARACTER SPACING", ),
    (5, 14): ("TEXT COLOUR", ),
    (5, 15): ("CHARACTER HEIGHT", ),
    (5, 16): ("CHARACTER ORIENTATION", ),
    (5, 17): ("TEXT PATH", ),
    (5, 18): ("TEXT ALIGNMENT", ),
    (5, 19): ("CHARACTER SET INDEX", ),
    (5, 20): ("ALTERNATE CHARACTER SET INDEX", ),
    (5, 21): ("FILL BUNDLE INDEX", ),
    (5, 22): ("INTERIOR STYLE", ),
    (5, 23): ("FILL COLOUR", ),
    (5, 24): ("HATCH INDEX", ),
    (5, 25): ("PATTERN INDEX", ),
    (5, 26): ("EDGE BUNDLE INDEX", ),
    (5, 27): ("EDGE TYPE", ),
    (5, 28): ("EDGE WIDTH", ),
    (5, 29): ("EDGE COLOUR", ),
    (5, 30): ("EDGE VISIBILITY", ),
    (5, 31): ("FILL REFERENCE POINT", ),
    (5, 32): ("PATTERN TABLE", ),
    (5, 33): ("PATTERN SIZE", ),
    (5, 34): ("COLOUR TABLE", ),
    (5, 35): ("ASPECT SOURCE FLAGS", ),
    (5, 36): ("PICK IDENTIFIER", ),
    (5, 37): ("LINE CAP", ),
    (5, 38): ("LINE JOIN", ),
    (5, 39): ("LINE TYPE CONTINUATION", ),
    (5, 40): ("LINE TYPE INITIAL OFFSET", ),
    (5, 41): ("TEXT SCORE TYPE", ),
    (5, 42): ("RESTRICTED TEXT TYPE", ),
    (5, 43): ("INTERPOLATED INTERIOR", ),
    (5, 44): ("EDGE CAP", ),
    (5, 45): ("EDGE JOIN", ),
    (5, 46): ("EDGE TYPE CONTINUATION", ),
    (5, 47): ("EDGE TYPE INITIAL OFFSET", ),
    (5, 48): ("SYMBOL LIBRARY INDEX", ),
    (5, 49): ("SYMBOL COLOUR", ),
    (5, 50): ("SYMBOL SIZE", ),
    (5, 51): ("SYMBOL ORIENTATION", ),

    (6, 1): ("ESCAPE", ),

    (7, 1): ("MESSAGE", ),
    (7, 2): ("APPLICATION DATA", ),

    (8, 1): ("COPY SEGMENT", ),
    (8, 2): ("INHERITANCE FILTER", ),
    (8, 3): ("CLIP INHERITANCE", ),
    (8, 4): ("SEGMENT TRANSFORMATION", ),
    (8, 5): ("SEGMENT HIGHLIGHTING", ),
    (8, 6): ("SEGMENT DISPLAY PRIORITY", ),
    (8, 7): ("SEGMENT PICK PRIORITY", ),

    (9, 1): ("APPLICATION STRUCTURE ATTRIBUTE", ),
}

OPER_PARSE = 0
OPER_LIST = 1
OPER_RENDER_SVG = 2

class Element():
    ''' CGM element container '''
    def __init__(self, class_num, id_num, method, desc, data):
        self.class_num = class_num
        self.id_num = id_num
        self.method = method
        self.desc = desc
        self.data = data
        self.priv = None

    def __str__(self):
        return "<Element " + self.render() + ">"

    def render(self):
        ''' Render as string '''
        return "(%d,%d) %s" % (self.class_num, self.id_num, self.desc[0])

class CGM_Data():
    '''
    ISO 8632-3 Computer Graphics Metafiles

    A built in extension mechanism looks for methods called:

        h_${element_class}_${element_id}_${element_name}()

    These methods do three different tasks, depending on the
    'oper' argument:

        0   Sanity-check.  Set self->error string if not kosher.
        1   Textual listing, output to self.fdo
        2   SVG rendering, output to self.fdo

    A simlar second level mechanism exists for Generalized Drawing Primitive
    which looks for:

	gdp_${gdp_identifier}()

    '''

    def __init__(self, data):
        self.text_anchor = "middle"
        self.vdc_extent = [0, 0, 1, 1]
        self.clip_rectangle = [0, 0, 1, 1]
        self.character_expansion_factor = 1
        self.character_orientation = [0, 0, 0, 0]
        self.text_alignment = [0, 0]
        self.pattern_size = 0
        self.line_width = 1
        self.elements = []
        self.fdo = None
        self.error = None
        self.error = self.parse(data)

    def parse(self, data):
        ''' Parse input data - return None or error string '''
        offset = 0
        data = bytearray(data)
        while True:
            if len(data) < 2:
                return "Not enough data"
            i = data.pop(0) << 8
            i |= data.pop(0)
            offset += 2

            length = i & 0x1f
            element_class = (i >> 12) & 0xf
            element_id = (i >> 5) & 0x7f

            desc = ISO8632_3.get((element_class, element_id))
            if desc is None:
                return "Unknown primitive (%d, %d)" % (element_class, element_id)
            ident = "(%d, %d) " % (element_class, element_id) + desc[0]

            if length == 0x1f:
                if len(data) < 2:
                    return "Not enough data"
                length = data.pop(0) << 8
                length |= data.pop(0)
                offset += 2
                if length & 0x8000:
                    return "Partitions not implemented " + ident
            if length > len(data):
                return "Not Enough data " + ident
            attr = "h_%d_%d" % (element_class, element_id)
            attr += "_" + desc[0].replace(' ', '_').lower()
            method = None
            if hasattr(self, attr):
                method = getattr(self, attr)
            element = Element(
                element_class,
                element_id,
                method,
                desc,
                data[:length]
            )
            if method:
                method(OPER_PARSE, element)
                if self.error:
                    return self.error
            self.elements.append(element)

            data = data[length:]
            offset += length
            if desc[0] == "END METAFILE":
                break
            if len(data) > 0 and offset & 1:
                data = data[1:]
                offset += 1
        if len(data) > 0:
            return "%d bytes left over" % len(data)
        return None

    def list(self, fo):
        ''' Textual listing into file handle fo'''
        self.fdo = fo
        for elem in self.elements:
            self.fdo.write(elem.render())
            if elem.method:
                elem.method(OPER_LIST, elem)
            else:
                self.fdo.write(" " + elem.data.hex())
            self.fdo.write("\n")
        self.fdo = None

    def render_svg(self, fo):
        ''' Render as SVG into file handle fo '''
        self.fdo = fo
        bbox = [0,0,1,1]
        self.svg_head(bbox)
        for elem in self.elements:
            if elem.method:
                elem.method(OPER_RENDER_SVG, elem)
        self.svg_tail()
        self.fdo = None

    def svg_head(self, bbox):
        ''' Produce SVG file prefix '''
        self.fdo.write('<?xml version="1.0" standalone="no"?>\n')
        self.fdo.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"\n')
        self.fdo.write(' "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
        self.fdo.write('<svg version="1.1"')
        self.fdo.write(' width="%d" height="%d"' % (1200, 1200))
        margin = .1
        bbox=list(self.clip_rectangle)
        bbox[1] *= -1
        bbox[3] *= -1
        bbox[0] -= margin * (bbox[2] - bbox[0])
        bbox[1] += margin * (bbox[1] - bbox[3])
        bbox[2] += margin * (bbox[2] - bbox[0])
        bbox[3] -= margin * (bbox[1] - bbox[3])
        self.fdo.write(' viewBox="%.6f %.6f' % (bbox[0], bbox[3]))
        self.fdo.write(' %.6f %.6f"' % (bbox[2] - bbox[0], bbox[1] - bbox[3]))
        self.fdo.write(' preserveAspectRatio="xMidyMid"\n')
        self.fdo.write(' xmlns="http://www.w3.org/2000/svg">\n')
        self.fdo.write('<g stroke-linecap="round" fill="none" stroke="black"')
        self.fdo.write(' stroke-width = "%f"' % (0.0010))
        self.fdo.write('>\n')

    def svg_tail(self):
        ''' Produce SVG file suffix '''
        self.fdo.write('</g>\n')
        self.fdo.write('</svg>\n')

    def single_sf(self, oper, elem):
        ''' Convenience function for single SF (string) argument '''
        if oper == OPER_PARSE:
            if elem.data[0] != len(elem.data) - 1:
                self.error = "Not enough data" + str(elem)
                return
        elif oper == OPER_LIST:
            self.fdo.write(' "' + elem.data[1:].decode("ISO8859-1") + '"')

    # pylint: disable=missing-function-docstring

    def h_0_1_begin_metafile(self, oper, elem):
        self.single_sf(oper, elem)

    def h_0_3_begin_picture(self, oper, elem):
        self.single_sf(oper, elem)

    def h_1_2_metafile_description(self, oper, elem):
        self.single_sf(oper, elem)

    def h_2_6_vdc_extent(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 32:
                self.error = "Wrong data length" + str(elem)
                return
            self.vdc_extent = struct.unpack(">4d", elem.data)
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.vdc_extent))

    def h_3_5_clip_rectangle(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 32:
                self.error = "Wrong data length" + str(elem)
                return
            self.clip_rectangle = struct.unpack(">4d", elem.data)
            self.line_width = math.fabs(self.clip_rectangle[2] - self.clip_rectangle[0]) / 1000
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.clip_rectangle))

    def h_4_1_polyline(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) % 16:
                self.error = "Not mod8 data" + str(elem)
                return
        elif oper == OPER_LIST:
            for i in range(0, len(elem.data), 16):
                a = struct.unpack(">dd", elem.data[i:i+16])
                self.fdo.write(' %9.6f,%9.6f' % (a[0], -1 * a[1]))
        elif oper == OPER_RENDER_SVG:
            self.fdo.write('<polyline points="')
            for i in range(0, len(elem.data), 16):
                a = struct.unpack(">dd", elem.data[i:i+16])
                self.fdo.write(' %9.6f,%9.6f' % (a[0], -1 * a[1]))
            self.fdo.write('" stroke-width="%g"' % self.line_width)
            self.fdo.write(' stroke="%s"/>\n' % "#000000")

    def h_4_4_text(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) <= 19:
                self.error = "Not enough data" + str(elem)
                return
            d = struct.unpack(">ddhB", elem.data[:19])
            if len(elem.data) != d[-1] + 19:
                self.error = "Not enough data" + str(elem)
                return
            t = elem.data[19:19+d[-1]].decode("ISO8859-1")
            elem.priv = (*d, t)
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(elem.priv))
        elif oper == OPER_RENDER_SVG:
            self.fdo.write('<text')
            self.fdo.write(' font-family="Verdana"')
            self.fdo.write(' font-size="%g"' % max(self.character_orientation))
            self.fdo.write(' x="%g"' % elem.priv[0])
            self.fdo.write(' y="%g"' % (-elem.priv[1]))
            self.fdo.write(' text-anchor="%s"' % self.text_anchor)
            self.fdo.write('>' + html.escape(elem.priv[4]) + '</text>\n')

    def h_4_7_polygon(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) == 0 or len(elem.data) % 16:
                self.error = "Not mod8 data" + str(elem)
                return
        elif oper == OPER_LIST:
            for i in range(0, len(elem.data), 16):
                a = struct.unpack(">dd", elem.data[i:i+16])
                self.fdo.write(' %9.6f,%9.6f' % (a[0], -1 * a[1]))
        elif oper == OPER_RENDER_SVG:
            self.fdo.write('<polyline points="')
            for i in range(0, len(elem.data), 16):
                a = struct.unpack(">dd", elem.data[i:i+16])
                if not i:
                    start_point = a
                self.fdo.write(' %9.6f,%9.6f' % (a[0], -1 * a[1]))
            self.fdo.write(' %9.6f,%9.6f' % (start_point[0], -1 * start_point[1]))
            self.fdo.write('" stroke="%s"/>\n' % "#000000")

    def gdp_polyline(self, elem):
        self.fdo.write('<polyline points="')
        for i in range(0, len(elem.priv[2]), 2):
            a = elem.priv[2][i:i+2]
            self.fdo.write(' %9.6f,%9.6f' % (a[0], -1 * a[1]))
        self.fdo.write('" stroke-width="%g"' % (2*self.line_width))
        self.fdo.write(' stroke="%s"/>\n' % "#ff0000")

    def h_4_10_generalized_drawing_primitive(self, oper, elem):
        if oper == OPER_PARSE:
            length = len(elem.data)
            if length <= 4:
                self.error = "Wrong data length" + str(elem)
                return
            a = struct.unpack(">HH", elem.data[:4])
            length = 4 + 16 * a[-1]
            if len(elem.data) < length + 1 or elem.data[length] != len(elem.data[length+1:]):
                self.error = "Wrong data length" + str(elem)
                return
            points = struct.unpack(">" + "dd" * a[1], elem.data[4:length])
            elem.priv = (*a, points, elem.data[length+1:])
            attr = "gdp_%d" % a[0]
            if hasattr(self, attr):
                elem.method = getattr(self, attr)
                elem.method(oper, elem)
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(elem.priv[:-1]) + ' ' + elem.priv[-1].hex())
        elif oper == OPER_RENDER_SVG:
            self.gdp_polyline(elem)

    def h_5_12_character_expansion_factor(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 8:
                self.error = "Wrong data length" + str(elem)
                return
            self.character_expansion_factor = struct.unpack(">d", elem.data)[0]
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.character_expansion_factor))

    def h_5_16_character_orientation(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 32:
                self.error = "Wrong data length" + str(elem)
                return
            self.character_orientation = struct.unpack(">4d", elem.data)
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.character_orientation))

    def h_5_18_text_alignment(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 4:
                self.error = "Wrong data length" + str(elem)
                return
            self.text_alignment = struct.unpack(">HH", elem.data)
            self.text_anchor = [
                "start",
                "start",
                "middle",
                "end",
                "start",
            ][self.text_alignment[0]]
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.text_alignment))

    def h_5_33_pattern_size(self, oper, elem):
        if oper == OPER_PARSE:
            if len(elem.data) != 32:
                self.error = "Wrong data length" + str(elem)
                return
            self.pattern_size = struct.unpack(">4d", elem.data)
        elif oper == OPER_LIST:
            self.fdo.write(' ' + str(self.pattern_size))


if __name__ == "__main__":

    import sys

    #b = open("/critter/aa/dde/d376f27e72.bin", "rb").read()
    #b = open("/critter/aa/dde/6529e6e65f.bin", "rb").read()
    #b = open("/critter/aa/dde/1349e23e26.bin", "rb").read()
    #b = open("/critter/aa/dde/00741f726a.bin", "rb").read()
    #b = open("/critter/aa/dde/aaffcef473.bin", "rb").read()
    #b = open("/critter/aa/dde/a8873bdfef.bin", "rb").read()
    #b = open("/critter/aa/dde/9c46bf7a74.bin", "rb").read()
    #b = open("/critter/aa/dde/81ddc38fd3.bin", "rb").read()
    #b = open("/critter/aa/dde/12fadd87c9.bin", "rb").read()
    b = open("/critter/aa/dde/00677d0d9d.bin", "rb").read()

    cgm = CGM_Data(b)
    print(cgm.error)
    cgm.list(sys.stdout)
    cgm.render_svg(open("/tmp/_.svg", "w"))
