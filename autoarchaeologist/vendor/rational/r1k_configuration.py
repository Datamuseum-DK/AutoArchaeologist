'''
   Rational R1000 .M200_CONFIG Configuration files
   -----------------------------------------------

'''

from ...generic import hexdump

FIELDS = [
    (0x002, 1, 'Allow operator to enter CLI immediately'),
    (0x003, 1, 'Allow editing of configuration'),
    (0x004, 1, 'Allow operator to enter CLI prior to starting the cluster'),
    (0x005, 1, 'Load kernel layer subsystems only'),
    (0x02a, 1, 'Auto boot the kernel debugger'),
    (0x02b, 1, 'Wait for remote debugging on kernel crashes'),
    (0x02c, 1, 'Call Rational on kernel crash'),
    (0x02f, 1, 'Auto boot the environment elaborator'),
    (0x030, 1, 'Auto boot the kernel'),
    # (0x032, 1, 'Should this configuration query for microcode when booting'),
]

# See: R1000_Knowledge_Transfer_Manual.pdf pdf pg27 '''
ENTRIES = [
    "MICROCODE",
    "ADA_BASE",
    "MACHINE_INTERFACE",
    "KERNEL_DEBUGGER_IO",
    "KERNEL_DEBUGGER",
    "KERNEL",
    "ENVIRONMENT_DEBUGGER",
    "ABSTRACT_TYPES",
    "MISCELLANEOUS",
    "OS_UTILITIES",
    "ELABORATOR_DATABASE",
]

class R1kM200ConfigFile():
    ''' Configuration Files '''

    def __init__(self, this):
        if not this.has_type("M200_CONFIG"):
            return
        if len(this) > 1024:
            return
        if this[1] != 3:
            return
        print("R1K_CONFIG", this)
        this.add_interpretation(this, self.render)

    def render(self, fo, this):
        ''' ... '''
        swapped = bytearray([0] * len(this))
        for idx, i in enumerate(this):
            swapped[idx^1] = i
        fo.write("<H3>R1K Configuration</H3>\n")
        fo.write("<pre>\n")
        adr = 0
        for idx, length, txt in sorted(FIELDS):
            if idx > adr:
                hexdump.hexdump_to_file(swapped[adr:idx], fo, offset = adr)
            if length == 1:
                fo.write(("%04x  %02x -- " % (idx, swapped[idx])) + txt + "\n")
            else:
                hexdump.hexdump_to_file(swapped[idx:idx+length], fo, offset = idx)
            adr = idx + length
        for i in range(11):
            txt = "%04x  %02x %02x '" % (adr, swapped[adr], swapped[adr + 1])
            for j in range(2, 32):
                if not swapped[adr + j]:
                    break
                txt += "%c" % swapped[adr + j]
            fo.write(txt + "' -- " + ENTRIES[i] + "\n")
            adr += 32
        if adr < len(swapped):
            if max(swapped[adr:]):
                hexdump.hexdump_to_file(swapped[adr:], fo, offset = adr)
            else:
                fo.write("%04x  00[0x%x]\n" % (adr, len(swapped) -adr))
        fo.write("</pre>\n")
