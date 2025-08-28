#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Render a unix mode word in standard ls(1) rwxrwxrwx format
'''

import time

class UnixStat():
    ''' Default unix mode bits '''
    S_ISFMT = 0o170000
    S_IFBLK = 0o060000
    S_IFDIR = 0o040000
    S_IFCHR = 0o020000
    S_IFPIP = 0o010000
    S_IFREG = 0o100000

    S_ISUID = 0o004000
    S_ISGID = 0o002000
    S_ISVTX = 0o001000
    S_IRUSR = 0o000400
    S_IWUSR = 0o000200
    S_IXUSR = 0o000100
    S_IRGRP = 0o000400
    S_IWGRP = 0o000200
    S_IXGRP = 0o000100
    S_IROTH = 0o000400
    S_IWOTH = 0o000200
    S_IXOTH = 0o000100

    def timestamp(self, time_t):
        ''' Render a time_t '''
        mtime = time.gmtime(time_t)
        return time.strftime("%Y-%m-%dT%H:%M:%S", mtime)

    def mode_bits(self, mode):
        ''' Render a st_mode '''
        txt = {
            self.S_IFPIP: "p",
            self.S_IFCHR: "c",
            self.S_IFDIR: "d",
            self.S_IFBLK: "b",
            self.S_IFREG: "-",
            0: "",
        }.get(mode & self.S_ISFMT)
        if txt is None:
            txt = "{%o}" % (mode & self.S_ISFMT)
        txt += "r" if mode & self.S_IRUSR else '-'
        txt += "w" if mode & self.S_IWUSR else '-'
        if mode & self.S_IXUSR and mode & self.S_ISUID:
            txt += "s"
        elif mode & self.S_IXUSR:
            txt += "x"
        else:
            txt += "-"
        txt += "r" if mode & self.S_IRGRP else '-'
        txt += "w" if mode & self.S_IWGRP else '-'
        if mode & self.S_IXGRP and mode & self.S_ISGID:
            txt += "s"
        elif mode & self.S_IXUSR:
            txt += "x"
        else:
            txt += "-"
        txt += "r" if mode & self.S_IROTH else '-'
        txt += "w" if mode & self.S_IWOTH else '-'
        if mode & self.S_ISVTX and mode & self.S_IXOTH:
            txt += "t"
        elif mode & self.S_ISVTX:
            txt += "T"
        else:
            txt += "-"
        return txt

stat = UnixStat()
