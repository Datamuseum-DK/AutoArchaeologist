
Collections
===========

AA has code to conveniently pull in artifacts from certain
public collections of historical computer artifacts.

Collections will cache the downloaded files in a directory which
can be specified directly in the call with a ``cache_dir`` argument,
with a ``cache_dir`` argument to the excavation or with the
environment variable ``AUTOARCHAEOLOGIST_CACHE_DIR``.

If no cache dir is specified, python's default tempdir is used.

.. toctree::
   :maxdepth: 2
   :caption: Supported collections:

   datamuseum_dk.rst
   bitsavers_org.rst
