#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   USER_DATA enumeration as seen in kernel CLI show_space_info
   ===========================================================

   "EEDB_File_Generic" is only seen in r1k_dfs ⟦bc0ad4cb9⟧ aka »1037331.SEG«


'''

user_data_strings = {
    0x03c: "Segment.index_block",
    0x03d: "Catalog.index_block",
    0x061: "mv_code_seg",
    0x062: "some_heap",
    0x063: "Heap_Manager_Generic default",
    0x064: "Temp_Heap default",
    0x065: "Polymorphic_File default",
    0x066: "Object_Id_Io default",
    0x06e: "EEDB",
    0x06f: "Name_Allocator",
    0x070: "Poly_File.Directory",
    0x071: "Low_Level_Action",
    0x072: "Job_Manager accounting",
    0x073: "Job_Segment.Get",
    0x074: "Code_Segment_Manager.Open",
    0x075: "EEDB_File_Generic.Code_Segment_Ops.Create",
    0x076: "Testbed_User_Interface..Code_Segment_Ops.Creat",
# 0x078-0x095 -> code@ 0x207b	"Manager" ?  
# 0x096-0x0b3 -> code@ 0x2083	"Data" ?
    0x0c8: "AOE session maps",
    0x0c9: "Session heap",
    0x0ca: "Search_List",
    0x0cb: "Library OE",
    0x0cc: "Directory subclass keys",
    0x0cd: "Image_Database",
    0x0ce: "Links OE temporary",
    0x0cf: "Activity OE image",
    0x0d0: "Activity OE storage",
    0x0d1: "Comp.Promote temporary",
    0x0d2: "Links OE image",
    0x0d3: "Switches OE image",
    0x0d4: "Switches OE storage",
    0x0d5: "Core_Editor initialization",
    0x0d6: "Core_Editor interpreter",
    0x0d7: "Image.Image data",
    0x0d8: "Image.Line_Buffer",
    0x0d9: "Xref",
    0x0da: "Ada_Oe (object tree?)",	# '?' in original
    0x0db: "File_Utilities",
    0x0dc: "System_Backup",
    0x0dd: "Session_Switches system state",
    0x0de: "OM_Tests Test_Backdoor",
    0x0df: "OM_Tests Test_Object_Conversions",
    0x0e0: "OM_Tests Test_Temp_Heap",
    0x0e1: "Session_Switches session state",
    0x0e2: "Ada_Editor_Interface.Execution",
    0x0e3: "Image: Permanent editor buffers",
    0x0e4: "Image: Permanent editor buffer map",
    0x0e5: "Help OE data",
    0x0e6: "Object_Set_Editor",
    0x0e7: "AOE session garbage diana unit",
    0x0e8: "Command OE session command heap",
    0x0e9: "Temp_Ada_Heap default",
    0x0ea: "Ada_Editor_Interface.Execution command heap pool",
    0x0eb: "Key_To_Command_Parser keymap space",
    0x0ec: "Key_To_Command_Name.Diana_Utilities temp_key_cache",
    0x0ed: "Ada Object Editor comment heap",
    0x0ee: "Command Object Editor comment hea",
    0x0ef: "Work Order Regression Tests temporary storage",
    0x0f0: "Middle pass debugging tools",
    0x0f1: "Work_Order_List_OE image storage",
    0x0f2: "Work_Order_OE image storage",
    0x0f3: "Venture_OE image storage",
    0x0f4: "Mail OE image storage",
    0x0f5: "Mail OE name maps",
    0x0f6: "Naming iterators and Work Order Archive Processin",
    0x0f7: "Diana Object Editor",
    0x0f8: "Design Facility Preview Object Editor",
    0x0f9: "Design Facility Format Heap",
    0x0fa: "Image Tree Consistency Checker",
    0x0fb: "Archived Code OE",
    0x0fc: "Completion OE",
    0x0fd: "Spelling OE",
    0x0fe: "Command Interpreter",
    0x0ff: "X Library",
    0x100: "Design OE",
    0x101: "DTIA",
    0x3fe: "fixup spaces from Segmented_Heap_Object_Manager_Generic",
    0x3ff: "fixup spaces from Kernel_Command_Interpreter",
}

def user_data_to_string(x):
    t = user_data_strings.get(x)
    if t:
        return t
    if 0x078 <= x <= 0x095:
        return "?Manager"
    if 0x096 <= x <= 0x0b3:
        return "?Data"
    if 0x200 <= x <= 0x2ff:
        return "Job_Segment for Job"
    return "unknown(0x03x)" % x
