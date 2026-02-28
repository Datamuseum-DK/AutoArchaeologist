#!/usr/bin/env python3

'''
   Intergraph default examiners
   ============================

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor import intergraph
       …
       intergraph.defaults(self)

   Contents
   --------

   .. toctree::
       :maxdepth: 1

       diskpar.rst
   
'''

from . import diskpar

def defaults(exc):
    exc.add_examiner(diskpar.IntergraphDiskPar)
