IBM 6580 DisplayWriter floppy disks
===================================

The IBM 6580 Displaywriter was a microprocessor based textprocessing
system which could also be connected as a terminal to "real" IBM
computers.  In many ways the Displaywriter was IBM's first response
to CP/M based microcomputers.

This examiner is at best a prototype:  No documentation of the
floppy layout could be located, so this examiner was written "cold"
based on a single floppydisk image.

Some hints if you want to work on this:
---------------------------------------

I'll keep the floppy image around, email me if you want a copy.

The character set is (an extended variant of) EBCDIC.

The floppy disk has GA21-9128 label with a single file named "WPE",
and it looks like the filesystem is based on block number in that file.

Record number 1872, which is located at CHS=(37, 0, 1) contains the
"superblock", identified by the string "EHL1" four bytes into the sector.

The superblock is the root in some kind of tree-ish structure, where all
records start with a Be16 length and a Octet record type.  Some of the
records span sectors.
