'''
   Hexdumping functions
'''

def hexdump(this, html=True):
    ''' Hexdump an artifact '''
    total = len(this)
    for i in range(0, total, 16):
        txt = "%04x " % i
        for j in range(min(16, total - i)):
            txt += " %02x" % this[i + j]
        if j < 15:
            txt += "   " * (15 - j)
        txt += "  |"
        for j in range(min(16, total - i)):
            k = this[i + j]
            if html and k == 0x3c:
                txt += "&lt;"
            elif html and k == 0x26:
                txt += "&amp;"
            elif 32 <= k <= 126:
                txt += "%c" % k
            else:
                txt += " "
        if j < 15:
            txt += " " * (15 - j)
        txt += "  |"
        yield txt

def hexdump_to_file(this, fo, *args, **kwargs):
    ''' Hexdump to a file '''
    for i in hexdump(this, *args, **kwargs):
        fo.write(i + "\n")
