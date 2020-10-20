'''
   AR(1) format
'''

import autoarchaeologist

import struct

class Ar():

    def __init__(self, this):
        if len(this) < 30:
            return
        words = struct.unpack("<H", this[:2])
        if words[0] != 0o177535:
            return
        self.this = this
        this.type = "Ar_file"
        this.add_note("Ar_file")
        offset = 2
        a = this.slice(0,2)
        a.type = "AR magic"
        while offset < len(this):
            words = struct.unpack("<14sLHHHHH", this[offset:offset+28])
            name = words[0].rstrip(b'\x00').decode("ASCII")
            a = this.slice(offset, 28)
            a.type = "AR header"
            offset += 28
            i = words[-2] << 16
            i |= words[-1]
            a = this.slice(offset, i)
            a.add_note("AR member")
            try:
                a.set_name(this.named + ":" + name)
            except autoarchaeologist.core_classes.DuplicateName:
                a.add_note(this.named + ":" + name)
            offset += i
