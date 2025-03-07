#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license


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

OBJ_SUBCLASS = {
    0: "NIL",
    2: "SUBSYSTEM",
    3: "DIRECTORY",
    4: "SUBSYSTEM",
    5: "SPEC_VIEW",
    6: "LOAD_VIEW",
    8: "GENERIC_PROCEDURE",
    9: "GENERIC_FUNCTION",
    10: "GENERIC_PACKAGE",
    12: "PACKAGE_INSTANTIATION",
    13: "PACKAGE_SPEC",
    17: "PROCEDURE_SPEC",
    21: "FUNCTION_SPEC",
    28: "PROCEDURE_BODY",
    29: "FUNCTION_BODY",
    31: "TASK_BODY",
    32: "PACKAGE_BODY",
    39: "COMPILATION_UNIT",
    42: "TEXT",
    43: "BINARY",
    46: "ACTIVITY",
    47: "SWITCH",
    48: "SEARCH_LIST",
    49: "OBJECT_SET",
    51: "POSTSCRIPT",
    52: "SWITCH_DEFINITION",
    56: "MAIN_PROCEDURE_SPEC",
    57: "MAIN_PROCEDURE_BODY",
    61: "COMPATIBILITY_DATABASE",
    62: "LOADED_PROCEDURE_SPEC",
    63: "LOADED_FUNCTION_SPEC",
    66: "COMBINED_VIEW",
    70: "CMVC_DATABASE",
    71: "DOCUMENT_DATABASE",
    72: "CONFIGURATION",
    80: "CMVC_ACCESS",
    555: "BINARY_GATEWAY",
    597: "REMOTE_TEXT_GATEWAY",
}

def ObjRef(cls, nbr, subcls):
    i = OBJ_CLASS.get(cls, "%d" % cls)
    j = OBJ_SUBCLASS.get(subcls, None)
    if not j:
        print("MISS", subcls)
        j = "%d" % subcls
    return ("[" + i + ",%d,1]" % nbr).ljust(24) + " (" + j + ")"

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
