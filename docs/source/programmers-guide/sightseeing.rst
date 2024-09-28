Sightseeing
===========

I'm going to point out some specific source files which may be worth
studying for what they do and how they do it.

``vendor/ibm/ga21_9128.py``
---------------------------

IBM midrange systems used 8" floppy disks for backup and data exchange
and files could easily be so big, that they would not fit on a single
floppy disk.

This class reads the headers from the floppies, tries to match them
into multi-floppy "volumes", and assembles the files from whatever
many floppies they were stored on.

The volumes have interpretations on the front page, because where else
could they go, when they span multiple top-level artifacts ?
