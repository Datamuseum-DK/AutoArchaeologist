
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
