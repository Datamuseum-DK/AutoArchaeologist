#!/usr/bin/env python3
#
# SPDX-License-Identifier: BSD-2-Clause
#
# See LICENSE file for full text of license

'''
    AutoArchaeologist Namespace Class
    ---------------------------------

    `NameSpace` is for implementing the interior name spaces of
    filesystem and other directory-like structures.

    We represent namespaces as a directed graph identified by a
    single "root" Artifact, but impose no limitations on cycles
    in the graph or how NameSpace nodes map to Artifacts.

    Because all byte-identical Artifacts collapse into one, it is
    the rule rather than exception that Artifacts are present in
    multiple namespaces.

    Experience so far has shown that using NameSpace as a parent
    class does not make anything easier, but nontheless all attributes
    have been prefixed "ns_" to make it easier.

'''

import html

class NameSpaceError(Exception):
    ''' ... '''

class NameSpace():

    '''
        NameSpace
        ---------

	A node in a NameSpace graph.

    '''

    KIND = "Namespace"
    TABLE = (
        ("l", "name"),
        ("l", "artifact"),
    )

    def __init__(
        self,
        name = None,		# The leaf name of this node
        parent = None,		# The parent of this node
        this = None,		# The artifact named by this node
        separator = "/",	# The path separator for children of this node
        root = None,		# The artifact in which the name-space lives.
        priv = None,		# The artifact in which the name-space lives.
    ):
        self.ns_children = []
        self.ns_name = name
        self.ns_parent = None
        self.ns_separator = separator
        self.ns_this = None
        self.ns_root = None
        self.ns_priv = priv
        if root:
            self.ns_set_root(root)
        if parent:
            parent.ns_add_child(self)
        if this:
            assert parent
            self.ns_set_this(this)

    def __lt__(self, other):
        return self.ns_path() < other.ns_path()

    def __repr__(self):
        return '<NS ' + str(self.ns_root) + " " + self.ns_path() + '>'

    def __iter__(self):
        yield from self.ns_children

    def ns_set_root(self, root):
        ''' Set the root artifact '''
        if self.ns_root == root:
            return
        if self.ns_root:
            raise NameSpaceError("Root already set")
        if self.ns_parent:
            raise NameSpaceError("Root and Parent are exclusive")
        self.ns_root = root
        root.ns_roots.append(self)

    def ns_set_this(self, this):
        ''' Set this nodes artifact '''
        if self.ns_this == this:
            return
        assert self.ns_this is None
        self.ns_this = this
        this.add_namespace(self)

    def ns_path_recurse(self):
        ''' Get the parent path, including separator, to this node '''
        if not self.ns_parent:
            pfx = ""
        else:
            pfx = self.ns_parent.ns_path_recurse()
        return pfx + self.ns_name + self.ns_separator

    def ns_path(self):
        ''' Get the path to this node '''
        if not self.ns_parent:
            return self.ns_name
        return self.ns_parent.ns_path_recurse() + self.ns_name

    def ns_render(self):
        ''' Return path and summary for interpretation table '''
        path = self.ns_path()
        if self.ns_this:
            return [
                html.escape(path),
                self.ns_this,
                ]
        return [ path, None ]

    def ns_add_child(self, child):
        ''' Add an child under this node'''
        assert isinstance(child, NameSpace)
        self.ns_children.append(child)
        child.ns_parent = self
        child.ns_root = self.ns_root
        if child.ns_separator is None and self.ns_separator is not None:
            child.ns_separator = self.ns_separator

    def ns_recurse(self, level=0):
        ''' Recuse through the graph '''
        yield level, self
        for child in sorted(self.ns_children):
            yield from child.ns_recurse(level+1)

    def ns_html_plain(self, file, this):
        ''' Render recursively with H3 header '''
        if not self.ns_children:
            return

        if self.KIND:
            file.write("<H3>" + self.KIND + "</H3>\n")
        self.ns_html_plain_noheader(file, this)

    def ns_html_plain_noheader(self, file, _this):
        ''' Render recursively - just the substance '''
        file.write("<div>")

        tbl = [x.ns_render() for y, x in self.ns_recurse() if y > 0]
        for i in tbl:
            this = i[-1]
            if this is not None:
                i[-1] = file.str_link_to_that(this)
                i[-1] += " " + this.summary(notes=True, descriptions=False, types=True)
            else:
                i[-1] = "«none»"
        cols = max(len(x) for x in tbl)
        i = min(len(x) for x in tbl)
        if i != cols:
            print("WARNING: Namespace as uneven table", min, cols)
            for x in tbl:
                while len(x) < cols:
                    x.append("UNEVEN_TBL")
        colwidth = []
        for i in range(cols):
            colwidth.append(max(len(str(x[i])) for x in tbl))

        file.write('<table>\n')

        align = [x[0] for x in self.TABLE]
        hdr = [x[1] for x in self.TABLE]
        while len(align) < cols:
            align.insert(0, "l")
            hdr.append("-")
        file.write('  <thead>\n')
        n = 0
        for algn, hdr in zip(align, hdr):
            if len(str(hdr)) > colwidth[n] + 3:
                algn = "v"
            n += 1
            file.write('      <th class="' + algn + '">' + str(hdr) + '</th>\n')
        file.write('  </thead>\n')

        file.write('  <tbody>\n')
        for row in tbl:
            file.write('    <tr class="stripe">\n')
            for colno, col in enumerate(row):
                if col is None:
                    col = '-'
                file.write('      <td class="' + align[colno] + '">' + str(col) + '</td>\n')
            file.write('    </tr>\n')
        file.write('  </tbody>\n')
        file.write('</table>\n')
        file.write("</div>")

    def ns_find(self, names, cls=None, **kwargs):
        ''' Find a path, optionally creating nodes '''
        while names and names[-1] == '':
            names.pop(-1)
        found = list(self.ns_lookup(names[0]))
        if not found and cls is None:
            return None
        if not found:
            found = cls(name = names[0], parent = self, **kwargs)
        else:
            found = found[0]
        if len(names) > 1:
            return found.ns_find(names[1:], cls=cls, **kwargs)
        return found

    def ns_lookup(self, name):
        ''' Look a name up in this namespace '''
        for i in self.ns_children:
            if i.ns_name == name:
                yield i

    def ns_lookup_peer(self, name):
        ''' Look a name up in the parent namespace '''
        if self.ns_parent:
            yield from self.ns_parent.ns_lookup(name)
