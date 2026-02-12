HP LIF filesystems
==================

LIF is a filesystem used on both HP computers and HP test-equipment, and it
exists in a number o minor variations.

Files are identified by filename and have a 16 bit type number, for which
no authoritative directory seem to exist.

LIF filesystems always start with the first sector on the disk media, as
seen by the HP product, and the ``LifFileSystem`` class makes that assumption.

Harddisks such as HP9134 can implement various partition schemes in hardware,
typically configured with DIP switches and with no on-disk partition-table.

The ``LifHardDisk`` examiner searches for LIF filesystems at all 256 byte boundaries,
and if candidates are found at non-zero offsets, will partition the artifact
accordingly, and hint ``LifFileSystem`` on the created children.

References:
-----------

https://www.hp9845.net/9845/projects/hpdir/

https://bitsavers.org/test_equipment/hp/64000/software/64941-90906_Jan-1984.pdf

Source:
-------

   vendor/hp/lif.py
