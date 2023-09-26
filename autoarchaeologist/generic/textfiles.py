#!/usr/bin/env python3

'''
   Generic Text files, based on type_case
'''

PATTERNS = {
    b'+++ Low_Level_Action Started':	'R1000 Log file',
}

class TextFiles():

    def __init__(self, this):
        if not this.has_note("ASCII"):
            return
        for k, v in PATTERNS.items():
            if k in this.tobytes():
                this.add_note(v)

        if this[:2] == b'%!':
            this.add_note("PostScript")

class TextFile():
    ''' General Text-File-Excavator '''

    VERBOSE = False

    MAX_TAIL = 128

    TYPE_CASE = None

    def __init__(self, this):
        self.this = this
        self.txt = []
        if self.TYPE_CASE:
            type_case = self.TYPE_CASE
        else:
            type_case = this.type_case
        for j in this.iter_bytes():
            slug = type_case.slugs[j]
            if slug.flags & type_case.INVALID:
                if self.VERBOSE:
                    print(this, "TextFile fails on", hex(j))
                return
            if slug.flags & type_case.IGNORE:
                continue
            self.txt.append(slug.long)
            if slug.flags & type_case.EOF:
                break
        if not self.credible():
            return
        tmpfile = this.add_utf8_interpretation(self.__class__.__name__)
        with open(tmpfile.filename, "w", encoding="utf-8") as file:
            file.write(''.join(self.txt))
        this.add_type(self.__class__.__name__)

    def credible(self):
        ''' Determine if result warrants a new artifact '''
        if len(self.this) - len(self.txt) > self.MAX_TAIL:
            return False
        if '\n' not in self.txt:
            return False
        return True
