'''
   Recognize RCSL numbers
   ----------------------
'''

RCLOCS = [ "AA", "RT", "GL" ]

def rcsl(a):
    ''' Look for a RCSL number '''
    b = bytearray()
    for i in a:
        if 32 <= i < 127 and i not in b'-:/':
            b.append(i)
        else:
            b.append(32)
    b = b.decode("ASCII")
    for i in RCLOCS:
        b = b.replace(i, i + " ")
    b = b.split()
    if len(b) > 3 and b[2] in RCLOCS:
        for n, i in enumerate(b[3]):
            if not '0' <= i <= '9':
                b[3] = b[3][:n]
                break
        return "-".join(b[:4])
    print("RCSL bad", b)
    return None

class RCSL():
    ''' Recognize RCSL numbers '''

    def __init__(self, this):

        i = 0
        while True:
            j = this[i:].tobytes().find(b'RCSL')
            if j == -1:
                break
            i += j
            that = rcsl(this[i:i+20])
            if that:
                this.add_note(that)
            i += 4
