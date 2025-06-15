#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Global R1K definitions
   ======================
'''

# See also: ⟦5d3bfb73b⟧
OBJECT_MANAGERS = {
    1: ("ADA", {
            2: "WORLD",
            3: "DIRECTORY",
            4: "SUBSYSTEM",
            5: "SPEC_VIEW",
            6: "LOAD_VIEW",
            8: "GENERIC_PROCEDURE",
            9: "GENERIC_FUNCTION",
            10: "GENERIC_PACKAGE",
            12: "PACKAGE_INSTANTIATION",
            13: "PACKAGE_SPEC",
            16: "PROCEDURE_INSTANTIATION",
            17: "PROCEDURE_SPEC",
            20: "FUNCTION_INSTANTIATION",
            21: "FUNCTION_SPEC",
            28: "PROCEDURE_BODY",
            29: "FUNCTION_BODY",
            31: "TASK_BODY",
            32: "PACKAGE_BODY",
            33: "UNRECOGNIZABLE",
            39: "COMPILATION_UNIT",
            56: "MAIN_PROCEDURE_SPEC",
            57: "MAIN_PROCEDURE_BODY",
            59: "MAIN_FUNCTION_BODY",
            62: "LOADED_PROCEDURE_SPEC",
            63: "LOADED_FUNCTION_SPEC",
            66: "COMBINED_VIEW",
            77: "SYSTEM_SUBSYSTEM",
        }
    ),
    2: ("DDB", {}),
    3: ("FILE", {
            0: "NIL",
            42: "TEXT",
            43: "BINARY",
            47: "SWITCH",
            46: "ACTIVITY",
            48: "SEARCH_LIST",
            49: "OBJECT_SET",
            51: "POSTSCRIPT",
            52: "SWITCH_DEFINITION",
            61: "COMPATIBILITY_DATABASE",
            70: "CMVC_DATABASE",
            71: "DOCUMENT_DATABASE",
            72: "CONFIGURATION",
            73: "VENTURE",
            74: "WORK_ORDER",
            80: "CMVC_ACCESS",
            83: "MARKUP",
            555: "BINARY_GATEWAY",
            597: "REMOTE_TEXT_GATEWAY",
        }
    ),
    4: ("USER", {}),
    5: ("GROUP", {}),
    6: ("SESSION", {}),
    7: ("TAPE", {}),
    8: ("TERMINAL", {}),
    9: ("DIRECTORY", {}),
    10: ("CONFIGURATION", {}),
    11: ("CODE_SEGMENT", {}),
    12: ("LINK", {}),
    13: ("NULL_DEVICE", {}),
    14: ("PIPE", {}),
    15: ("ARCHIVED_CODE", {}),
    16: ("PROGRAM_LIBRARY", {}),
    17: ("NATIVE_SEGMENT_MAP", {}),
}
