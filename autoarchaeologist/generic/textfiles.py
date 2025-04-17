#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
   Generic Text files, based on type_case
'''

class TextFile():
    ''' General Text-File-Excavator '''

    # print() why artifacts get rejected
    VERBOSE = False

    # No longer than this
    MAX_LENGTH = 4 << 20

    # Max octets after EOF
    MAX_TAIL = 2048

    # Always Use this TypeCase
    TYPE_CASE = None

    # How many different INVALID octets are acceptable
    INVALID_TOLERANCE = 5

    # How many INVALID octets are acceptable
    INVALID_COUNT = 100
    INVALID_RATIO = .05

    # How many lines must there be (= '\n' in output)
    MIN_LINES = 1

    def __init__(self, this):
        if this.children:
            return
        if len(this) > self.MAX_LENGTH:
            return

        if self.TYPE_CASE:
            type_case = self.TYPE_CASE
        else:
            type_case = this.type_case

        go_quietly_at = self.INVALID_TOLERANCE
        if self.VERBOSE:
            # Allow a few more to report what we failed on
            go_quietly_at += 10

        self.tolerance = []
        self.this = this
        self.eof_pos = None
        self.txt = []
        self.histogram = [0] * 256
        self.counts = {
            "IGNORE": 0,
            "INVALID": 0,
            "GOOD": 0,
        }
        for n, j in enumerate(this.iter_bytes()):
            self.histogram[j] += 1
            slug = type_case.slugs[j]
            if slug.flags & type_case.IGNORE:
                self.counts["IGNORE"] += 1
            elif slug.flags & type_case.INVALID:
                self.counts["INVALID"] += 1
                mark = "▶%02x◀" % j
                self.tolerance.append(mark)
                if len(self.tolerance) <= self.INVALID_COUNT:
                    self.txt.append(mark)
                elif len(self.tolerance) > go_quietly_at:
                    return
            else:
                self.counts["GOOD"] += 1
                self.txt.append(slug.long)
            if slug.flags & type_case.EOF:
                self.eof_pos = n
                break
        if not self.credible():
            return
        tmpfile = this.add_utf8_interpretation(self.__class__.__name__)
        with open(tmpfile.filename, "w", encoding="utf-8") as file:
            file.write(''.join(self.txt))
        this.add_type(self.__class__.__name__)

    def credible(self):
        ''' Determine if result warrants a new artifact '''
        if not self.credible_tolerance():
            return False
        if not self.credible_min_lines():
            return False
        if not self.credible_max_tail():
            return False
        if not self.credible_report_tolerated():
            return False
        return True

    def credible_tolerance(self):
        ''' Check INVALID slug tolerance '''
        if len(self.tolerance) > self.INVALID_RATIO * len(self.txt):
            return False
        if len(self.tolerance) > self.INVALID_COUNT:
            if self.VERBOSE:
                print(
                    self.this,
                    self.__class__.__name__,
                    "Fails on",
                    " ".join(self.tolerance[:self.INVALID_COUNT]),
                    len(self.txt),
            )
            return False
        return True

    def credible_report_tolerated(self):
        ''' In verbose mode report what we tolerated '''
        if self.VERBOSE and self.tolerance:
            k = []
            for i in sorted(set(self.tolerance)):
                j = self.tolerance.count(i)
                if j == 1:
                    k.append(i)
                else:
                    k.append(i + "*%d" % j)
            print(
                self.this,
                self.__class__.__name__,
                "Tolerated",
                " ".join(k),
            )
        return True

    def credible_max_tail(self):
        ''' Check amount of file behind EOF '''
        if self.MAX_TAIL is None or self.eof_pos is None:
            return True
        if len(self.this) - self.eof_pos > self.MAX_TAIL:
            if self.VERBOSE:
                print(
                    self.this,
                    self.__class__.__name__,
                    "Too much after EOF:",
                    len(self.this) - len(self.txt)
                )
            return False
        return True

    def credible_min_lines(self):
        ''' Check number of lines in output '''
        if self.MIN_LINES is None:
            return True
        lines = self.txt.count('\n')
        if lines < self.MIN_LINES:
            if self.VERBOSE and lines > 0:
                print(
                    self.this,
                    self.__class__.__name__,
                    "Too few lines:",
                    lines,
                )
            return False
        return True

class TextFileVerbose(TextFile):
    ''' General Text-File-Excavator '''

    VERBOSE = True
