#!/usr/bin/env python3

'''
   Intergraph default examiners
   ============================

   Usage
   -----

   .. code-block:: none

       from autoarchaeologist.vendor import intergraph
       …
       intergraph.default_examiners(self)

   Contents
   --------

   .. toctree::
       :maxdepth: 1

       diskpar.rst
   
'''

from . import diskpar

def default_examiners(exc):
    exc.add_examiner(diskpar.IntergraphDiskPar)

default = [
	diskpar.IntergraphDiskPar,
]
