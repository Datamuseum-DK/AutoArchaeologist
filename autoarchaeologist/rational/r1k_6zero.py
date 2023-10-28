'''
Segments which start with six zero-bits after the header are
very often ascii files.
'''

class R1k6ZeroSegment():
    ''' Look for ascii files with six zero bits prefix '''
    def __init__(self, this):
        if not this.has_note('R1k_Segment'):
            return
        bits = bin(int.from_bytes(b'\xff' + this[:17].tobytes(), 'big'))[10:]
        hdr0 = int(bits[:32], 2)
        hdr1 = int(bits[32:64], 2)
        hdr2 = int(bits[64:96], 2)
        hdr3 = int(bits[96:128], 2)
        hdr4 = int(bits[128:134], 2)
        if hdr4:
            return
        if hdr0 > hdr3:
            return
        if hdr2:
            return
        if hdr1 & 0xfff != 0xfff:
            return
        if hdr3 & 0xfff != 0xfff:
            return
        if (hdr0 + 0x7f - 134) % 8:
            return
        text = []
        a = (this[16] & 3) << 8
        hdr0 += 0x7f
        self.incomplete = 0
        for n, i in enumerate(this):
            hdr0 -= 8
            if hdr0 < 0:
                break
            if n > 16:
                a |= i
                char = (a >> 2) & 0xff
                a &= 3
                a <<= 8
                if 32 <= char <= 126:
                    text.append(b'%c' % char)
                elif char in (9, 10, 12, 13,):
                    text.append(b'%c' % char)
                else:
                    if n > 17:
                        print("6Z FAIL", this, "char 0x%02x" % i, n, hdr0)
                    if n > 1024:
                        self.incomplete = n
                        break
                    return
        if len(text) > 0:
            this.add_note("R1k6ZERO")
            self.that = this.create(bits=b''.join(text))
            self.that.add_note("R1k Text-file segment")
            this.add_interpretation(self, self.render_bits)
            if self.incomplete:
                this.add_interpretation(self, this.html_default_interpretation)

    def render_bits(self, fo, _this):
        ''' just a pointer to the new artifact '''
        fo.write('<H3>R1K Text file</H3>\n')
        fo.write('<pre>\n')
        fo.write('Please see content at' + self.that.summary() + '\n')
        if self.incomplete:
            fo.write('From approx 0x%x conversion failed\n' % self.incomplete)
        fo.write('</pre>\n')
