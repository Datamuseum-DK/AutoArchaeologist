'''
   Hexdumping functions
'''

def hexdump(this, html=True, width=16, prefix=""):
    ''' Hexdump an artifact '''
    total = len(this)
    for i in range(0, total, width):
        txt = prefix + "%04x " % i
        for j in range(min(width, total - i)):
            txt += " %02x" % this[i + j]
        if j < (width - 1):
            txt += "   " * ((width - 1) - j)
        txt += "  |"
        for j in range(min(width, total - i)):
            k = this[i + j]
            if html and k == 0x3c:
                txt += "&lt;"
            elif html and k == 0x26:
                txt += "&amp;"
            elif 32 <= k <= 126:
                txt += "%c" % k
            else:
                txt += " "
        if j < (width - 1):
            txt += " " * ((width - 1) - j)
        txt += "|"
        yield txt

def hexdump_to_file(this, fo, *args, **kwargs):
    ''' Hexdump to a file '''
    for i in hexdump(this, *args, **kwargs):
        fo.write(i + "\n")
