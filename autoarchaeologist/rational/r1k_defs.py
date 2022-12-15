
OBJ_CLASS = {
    1: "ADA",
    2: "DDB",
    3: "FILE",
    4: "USER",
    5: "GROUP",
    6: "SESSION",
    7: "TAPE",
    8: "TERMINAL",
    9: "DIRECTORY",
    10: "CONFIGURATION",
    11: "CODE_SEGMENT",
    12: "LINK",
    13: "NULL_DEVICE",
    14: "PIPE",
    15: "ARCHIVED_CODE",
}

class ObjClass():

    def __init__(self, val):
        self.val = val

    def __str__(self):
        i = OBJ_CLASS.get(val)
        if i:
            return i
        return "OBJCLASS(0x%x)" % self.val

class R1KSegment():
    ''' ... '''
    def __init__(self):
        self.tag = None
