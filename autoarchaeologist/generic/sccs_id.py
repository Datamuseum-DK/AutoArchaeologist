'''
   SCCS identifiers
   ----------------
'''

class SccsId():
    ''' Add a note for the first SCCS identifier '''
    def __init__(self, this):
        start = this.tobytes().rfind(b'@(#)')
        if start >= 0:
            j = bytearray()
            for i in this[start:]:
                if i in (0x00, 0x0a, 0x22, 0x3e, 0x5c):
                    break
                j.append(i)
            this.add_note(this.type_case.decode(j))
