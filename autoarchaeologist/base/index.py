#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    AutoArchaeologist Index
    ----------------------------

    Build a index for everything under a particular artifact

'''

import html

PAGE_SIZE = 1000

def safe_filename(filename):
    ''' Produce a safe filename '''
    i = []
    for j in filename.encode('utf-8'):
        if 48 <= j <= 57:
            i += "%c" % j
        elif 65 <= j <= 90:
            i += "%c" % j
        elif 97 <= j <= 122:
            i += "%c" % j
        else:
            i += "_%02x" % j
    return "".join(i)

class Entry():
    ''' An entry in the index: subject + N*artifact '''

    def __init__(self, key):
        self.key = key
        self.entries = set()
        self.spill = 0
        self.relpath = None

    def __len__(self):
        if self.spill:
            return self.spill + 1
        return len(self.entries)

    def __lt__(self, other):
        return self.key < other.key

    def add_to_entry(self, this):
        ''' Add an artifact '''
        self.entries.add(this)

    def produce_lines(self, fot):
        ''' Produce in the lines '''
        key = html.escape(self.key)
        i = [(this.summary(names=True), this) for this in self.entries]

        for summ, this in sorted(i):
            fot.write('<tr><td>' + key + '</td>')
            fot.write('<td class="s">')
            fot.link_to_that(this)
            fot.write(" " + summ + '</td>\n')
            fot.write('</tr>\n')
            key = ""

    def produce(self, fot):
        ''' Produce this entry in the index page '''
        if not self.spill:
            self.produce_lines(fot)
        else:
            key = html.escape(self.key)
            fot.write('<tr><td>' + key + '</td>')
            fot.write('<td>')
            fot.link_to(self.relpath, "%d entries" % len(self.entries))
            fot.write('</td></tr>')

class Tab():
    '''
       A Tab is a range of entries with a common prefix
    '''

    def __init__(self, hdr):
        self.hdr = hdr
        self.hhdr = html.escape(hdr)
        self.entries = {}
        self.file = None

    def __lt__(self, other):
        return self.hdr < other.hdr

    def __repr__(self):
        return "<Tab " + self.hdr + " " + str(len(self.entries)) + ">"

    def __len__(self):
        return sum(len(x) for x in self.entries.values())

    def add_entry(self, entry):
        ''' ... '''
        i = self.entries.get(entry.key)
        if not i:
            i = []
            self.entries[entry.key] = i
        i.append(entry)

    def split(self):
        '''
           If this Tab is too long for a page, split it with longer prefixes.
        '''
        width = len(self.hdr)
        while True:
            width += 1
            ntabs = {}
            fail = False
            for entries in self.entries.values():
                for entry in entries:
                    key = entry.key[:width]
                    ntab = ntabs.get(key)
                    if ntab is None:
                        ntab = Tab(key)
                        ntabs[key] = ntab
                    ntab.add_entry(entry)
                    if len(ntab) > PAGE_SIZE:
                        fail = True
                        break
                if fail:
                    break
            if fail:
                continue
            i = max(len(tab) for tab in ntabs.values())
            if i < 1.2 * PAGE_SIZE:
                break
        yield from ntabs.values()

    def produce(self, fot):
        ''' Produce as html, with anchor '''
        fot.write('<A name="IDX_%s"><H4>%s</H4></A>\n' % (self.hhdr, self.hhdr))
        fot.write("<table>\n")
        for entries in sorted(self.entries.values()):
            for entry in sorted(entries):
                entry.produce(fot)
        fot.write("</table>\n")

class Page():
    ''' ... '''

    def __init__(self, this):
        self.this = this
        self.tabs = []
        self.relpath = None
        self.cached_len = None

    def __len__(self):
        if self.cached_len is None:
            self.cached_len = sum(len(x) for x in self.tabs)
        return self.cached_len

    def __repr__(self):
        return "<Page " + self.range() + " %d>" % len(self)

    def update(self):
        ''' Page contents has changed '''
        self.cached_len = None

    def what(self):
        ''' Layout summary for debugging purposes '''
        first = "[" + str(len(self.tabs[0]))
        if len(self.tabs) == 1:
            return first + "]"
        last = str(len(self.tabs[-1])) + "]"
        if len(self.tabs) == 2:
            return first + "," + last
        return first + "(" + str(sum(len(x) for x in self.tabs[1:-1])) + ")" + last

    def make_filename(self, this):
        ''' Come up with filename '''
        i = safe_filename(self.tabs[0].hdr)
        if len(self.tabs) > 1:
            i += "__" + safe_filename(self.tabs[-1].hdr)
        self.relpath = self.this.basename_for("_index_" + i + ".html")

    def range(self):
        ''' What's in this page '''
        i = self.tabs[0].hdr
        if len(self.tabs) > 1:
            i += " … " + self.tabs[-1].hdr
        return i

    def produce(self, file):
        ''' Produce this page '''
        for tab in self.tabs:
            tab.produce(file)

class Index():
    ''' In index for an excavation or artifact '''

    def __init__(self, this):
        self.this = this
        self.entries = {}
        self.tabs = {}
        self.pages = []
        self.seen = set()
        self.collect(this)
        self.ptrs = None
        self.make_plan()
        if this.top == this:
            self.title = "Master Index"
        else:
            self.title = "Index for " + str(this)

    def __len__(self):
        return sum(len(x) for x in self.entries.values())

    def add_entry(self, key, this, what=""):
        ''' Add an entry to the index '''

        if len(key) == 0:
            print(this, "empty index key (%s)" % what)
            return
        i = self.entries.get(key)
        if i is None:
            i = Entry(key)
            self.entries[key] = i
        i.add_to_entry(this)

    def collect(self, this):
        ''' Collect what goes in the index '''

        for i in this.names:
            self.add_entry(i, this, "name")
        for i in this.iter_types():
            self.add_entry(i, this, "type")
        for note, val in this.iter_notes():
            for args in val:
                arg = args.get("args")
                if arg:
                    self.add_entry(note + ", " + str(arg), this, "note")
                else:
                    self.add_entry(note, this, "note")
        for i in this.children:
            if i not in self.seen:
                self.collect(i)
                self.seen.add(i)

    def make_plan(self):
        ''' Plan the page layout of the index '''

        # Spill everything
        for entry in self.entries.values():
            if len(entry) > 5:
                entry.spill = 5

        # Split into tabs
        for key, entry in self.entries.items():
            tab = self.tabs.get(key[0])
            if not tab:
                tab = Tab(key[0])
                self.tabs[key[0]] = tab
            tab.add_entry(entry)

        for tab in list(sorted(self.tabs.values())):
            if len(tab) < PAGE_SIZE * 1.2:
                continue
            del self.tabs[tab.hdr]
            #print(self.this, "split", tab.hdr)
            for ntab in tab.split():
                self.tabs[ntab.hdr] = ntab

        for tab in sorted(self.tabs.values()):
            page = Page(self.this)
            page.tabs.append(tab)
            page.update()
            self.pages.append(page)

        #print("CP", len(self.entries), len(self.pages))
        self.pages = self.combine_pages(self.pages)

    def imbalance(self, plist):
        ''' Calculate the page size imbalance '''

        assert len(plist) != 0
        return int(sum((len(x)-PAGE_SIZE)**2 for x in plist))

    def improve_pages(self, plist, imbalance):
        ''' Improve page layout '''

        # Combine small pages
        for i in range(0, len(plist) -1):
            if len(plist[i]) + len(plist[i + 1]) < PAGE_SIZE:
                plist[i].tabs += plist[i + 1].tabs
                plist.pop(i+1)
                plist[i].update()
                return True, plist

        # Try shuffling a tab further down
        for i in range(0, len(plist) - 1):
            plist[i + 1].tabs.insert(0, plist[i].tabs.pop(-1))
            plist[i].update()
            plist[i + 1].update()
            if self.imbalance(plist) <= imbalance:
                if len(plist[i]) == 0:
                    plist.pop(i)
                return True, plist
            plist[i].tabs.append(plist[i+1].tabs.pop(0))
            plist[i].update()
            plist[i + 1].update()

        if len(plist) <= 2:
            return False, plist

        # Absorb very small pages
        for pgno, page in enumerate(plist):
            if len(page) * 20 > PAGE_SIZE:
                continue
            print("ORPHAN INDEX PAGE", pgno, len(page), len(plist))
            if pgno == 0 or (pgno+1 < len(plist) and len(plist[pgno+1]) < len(plist[pgno-1])):
                while page.tabs:
                    plist[pgno + 1].tabs.insert(0, page.tabs.pop(-1))
                plist.pop(pgno)
                plist[pgno + 1].update()
                return True, plist
            if pgno == len(plist) - 1 or len(plist[pgno-1]) < len(plist[pgno+1]):
                while page.tabs:
                    plist[pgno - 1].tabs.append(page.tabs.pop(0))
                plist.pop(pgno)
                plist[pgno - 1].update()
                return True, plist

        return False, plist

    def combine_pages(self, plist):
        ''' Iteratively improve page layout '''

        again = True
        while again and len(plist) > 1:
            imbalance = self.imbalance(plist)
            #print(self.this, imbalance, len(plist), " ".join(page.what() for page in plist))
            again, plist = self.improve_pages(plist, imbalance)

        return plist

    def h2_line(self, file, extra=""):
        file.write('<H2>')
        if self.this.top == self.this:
            file.write('Master Index')
        else:
            file.write('Index for ')
            file.link_to_that(self.this)
        file.write(extra)
        file.write('</H2>\n')

    def produce_spills(self):
        ''' Produce the spill pages '''

        for entry in self.entries.values():
            if not entry.spill:
                continue
            i = safe_filename(entry.key)
            entry.relpath = self.this.basename_for("_index__" + i + ".html")
            title = self.title + ": " + html.escape(entry.key)
            with self.this.top.decorator.html_file(entry.relpath, title) as file:
                file.write("<pre>\n")
                file.link_to(self.this.top.relpath, "top")
                file.write("</pre>\n")
                self.h2_line(file, ": " + html.escape(entry.key))
                file.write('<table>\n')
                entry.produce_lines(file)
                file.write('</table>\n')

    def produce_index_header(self, fot, pgno=None):
        ''' Produce the index header line '''

        fot.write("Index: ")
        if pgno is not None and len(self.pages) > 1:
            if pgno > 0:
                fot.link_to(self.pages[pgno-1].relpath, "◀")
            fot.write(' {%s}' % html.escape(self.pages[pgno].range()))
            if pgno < len(self.pages) - 1:
                fot.write(" ")
                fot.link_to(self.pages[pgno+1].relpath, "▶")
            fot.write("   ")
        for ptr, page in self.ptrs:
            #fot.write('<A href="%s#IDX_%s">%s</A> ' % (page.file.link, ptr, ptr))
            fot.write(" ")
            fot.link_to(page.relpath + "#IDX_" + ptr, ptr)
        fot.write("\n")

    def produce(self, fot):
        ''' Produce the index '''

        cur_key = None
        self.ptrs = []

        for page in self.pages:
            page.make_filename(self.this)
            for tab in page.tabs:
                key = tab.hdr[:1]
                if key != cur_key:
                    self.ptrs.append([html.escape(key), page])
                    cur_key = key

        self.produce_spills()

        self.produce_index_header(fot)
        for pgno, page in enumerate(self.pages):
            if len(self.pages) == 1:
                title = self.title
            else:
                title = self.title + ": " + html.escape(page.range())
            with self.this.top.decorator.html_file(page.relpath, title) as file:
                file.write('<pre>')
                file.link_to(self.this.top.basename_for(self.this.top), "top")
                file.write('</pre>\n')
                self.produce_index_header(file, pgno=pgno)
                self.h2_line(file)
                page.produce(file)
