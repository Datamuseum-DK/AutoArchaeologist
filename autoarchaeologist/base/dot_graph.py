'''
   Build a dot(1) graph of the connectivity in a Octet- or BitView tree
'''

class DotGraph():
    '''
        Builds the graph, separate class so we can make it more fancy
        with layout and style(s) later.
    '''

    def __init__(self, out, bintree):
        self.out = out
        self.bintree = bintree
        self.n_edges = 0

    def head(self):
        ''' Emit the start of the dot syntax '''
        self.out.write("digraph {\n")
        self.out.write('rankdir="LR"\n')
        self.out.write('node [shape=box]\n')

    def walk(self):
        ''' Walk the bintree '''
        for leaf in self.bintree:
            leaf.dot_node(self)
        for leaf in self.bintree:
            leaf.dot_edges(self)

    def tail(self):
        ''' Emit the end of the dot syntax '''
        self.out.write("}\n")

    def add_edge(self, src, dst):
        ''' Add an edge from src (bintree.Leaf) to dst (int) '''
        self.out.write("A%x -> A%x\n" % (src.lo, dst))
        self.n_edges += 1

def add_interpretation(this, bintree):

    ''' Add a dot_graph to this of the tree in bintree '''

    fn = this.filename_for(suf=".dot")
    with open(fn.filename, "w", encoding="utf-8") as out:
        dot = DotGraph(out, bintree)
        dot.head()
        dot.walk()
        dot.tail()

        with this.add_html_interpretation('Dot Graph') as out:
            out.write('<A href="' + fn.link + '">')
            out.write('Graphviz dot(1) file (%d edges)' % dot.n_edges)
            out.write('</A>\n')
        print(this, "DOT: %d edges" % dot.n_edges)
