'''
   BitData
   =======

   Tools for dealing with data not on byte boundaries

   NB: Dont use these classes in new development

'''

class PackedBits():
    '''
    Take a sequence of octets apart, in arbitrary bit-width fields
    '''

    def __init__(self, octets):
        self.octets = octets
        self.index = 0

    def __len__(self):
        return len(self.octets) * 8 - self.index

    def get(self, bits):
        ''' Snip `bits` of from the left '''
        first_bit = self.index
        self.index += bits
        first_octet = first_bit >> 3
        last_octet = (self.index + 7) >> 3
        value = int.from_bytes(self.octets[first_octet:last_octet], byteorder='big')
        if self.index & 7:
            value = value >> (8 - (self.index & 7))
        return value & ((1 << bits) - 1)

class BitRecord():
    '''
    Record of bit-packed fields

    `field_spec` is a sequence of `(name, width_in_bits, visible)`
    the `name` becomes an attribute of `self`
    '''

    def __init__(
        self,
        field_spec,
        type_name="BitRecord",
        octets=None,
        bits=None
    ):
        if bits:
            assert octets is None
            packed_bits = bits
        else:
            packed_bits = PackedBits(octets)
        self._field_spec = field_spec
        self._type_name = type_name
        for name, length, _visible in field_spec:
            setattr(self, name, packed_bits.get(length))

    def __str__(self):
        return '<' + self._type_name + ' ' + self.render(show_tag=True) + '>'

    def render(
        self,
        show_tag=False,
        one_per_line=False,
        fixed_width=False,
        prefix="    ",
        show_all=False,
    ):
        ''' Return string rendering '''
        i = []
        fmt = "%x"
        for name, length, visible in self._field_spec:
            if show_all or visible:
                if fixed_width:
                    fmt = "%0" + "%dx" % ((length + 3) // 4)
                i.append((name, fmt % getattr(self, name)))
        if show_tag and not one_per_line:
            return ' '.join([x + "=" + y for x,y in i])
        if not one_per_line:
            return ' '.join([y for _x,y in i])
        if show_tag:
            return prefix + ('\n' + prefix).join([x + "=" + y for x,y in i])
        return prefix + ('\n' + prefix).join([y for _x,y in i])
