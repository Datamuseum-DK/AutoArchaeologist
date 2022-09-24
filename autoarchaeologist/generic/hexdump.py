'''
   Hexdumping functions
'''

def hexdump(this, html=True, width=16, prefix="", offset=0):
    ''' Hexdump an artifact '''
    txt1 = ""
    txt2 = ""
    for n, x in enumerate(this):
        i = n % width
        if not i:
            txt1 = prefix + "%04x " % (n + offset)
            txt2 = "  ┆"
        txt1 += " %02x" % x
        if html and x == 0x3c:
            txt2 += "&lt;"
        elif html and x == 0x26:
            txt2 += "&amp;"
        elif 32 <= x <= 126:
            txt2 += "%c" % x
        else:
            txt2 += " "
        if i == width - 1:
            yield txt1 + txt2 + "┆"
    i = len(this) % width
    if i:
        txt1 += "   " * (width - i)
        txt2 += " " * (width - i)
        yield txt1 + txt2 + "┆"

def hexdump_to_file(this, fo, *args, **kwargs):
    ''' Hexdump to a file '''
    for i in hexdump(this, *args, **kwargs):
        fo.write(i + "\n")
