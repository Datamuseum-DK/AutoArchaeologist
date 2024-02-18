# AutoArchaeologist

A Python Toolchest to dissect historic data media. 

The fundamental problem is how to explore the data from ancient and rare
computers, in a convenient and user-friendly way.

The AutoArchaeologist is a framework where plugins can be written to take
apart and present old data media, in a browser-friendly fashion.

## Getting started

To get a feel for how this works and ensure you've got everything set up,
we've included a sample file that can be excavated as an example:

```sh
python3 run_example.py
```

When you're ready to for further and process you own images use `run.py`.

## Using run.py

The various utilities that allow the extraction and processing of data are
designed to be composed into an Excavation that can be run against binary
images of disks and other media. Some standard excavations have been put
together in bundles ad exposed via a single `run` command.

Performing an exavation of a file is as simple as the following:

```sh
python3 run.py --excavator <excavator> <filename>
```

Usage information including the list of excavatos that are avalable as well as
other options will be output when running without arguments: `python3 run.py`.

## From the DDHF

# First Example: Commodore CBM900 Harddisk

Our first historic use of the AutoArchaeologist is now online:

https://datamuseum.dk/aa/cbm900

This is the harddisk from datamuseum.dk's rare and running Commodore CBM-900
UNIX computer (https://datamuseum.dk/wiki/Commodore/CBM900)

In this case, the code in `unix/v7_filesystem.py` recognizes this as a little
endian Version 7 unix filesystem, and creates artifacts for the individual
files in the filesystem.

The `generic/ascii.py` code spots which files are text files, and thus we can
see how few fortunes, the CBM-900 came with, back in 1984:

http://datamuseum.dk/aa/cbm900//5c/5caa31010.html

# Second Example: RegneCentralen GIER computer

The paper-tapes from this computer, like many other of 1950-1960
vintage, are not in ASCII but in a per-model, and in some cases,
per-installation character set.  The one on GIER isnt too bad
(https://datamuseum.dk/wiki/GIER/Flexowriter) but did cause a bit
of headache before we got a good HTML representation of overprinting
underlines and the "10" glyph.

GIER is of course the computer Peter Naur of Backus-Naur-Notatation
fame worked on, and his demonstration program is a good example of the output:

http://datamuseum.dk/aa/gier/9c/9cb418c94.html

# Third Example: Regnecentralen RC3600/RC7000

RC7000 was a Data General Nova with a "RC7000" sticker, RC3600 was
Regnecentralens own reimplementation, and they were as a sort of swiss
army-knife computer doing everything from industrial control and monitoring,
to teaching programming in high-schools.

We have a rich software archive for these computers, and making sense
of them requires quite a number of "examiners".

Here is a saved COMAL program (https://datamuseum.dk/wiki/COMAL) to
solve second degree equations, written by a high-school student in 1981:

http://datamuseum.dk/aa/rc3600/7b/7b059e3b3.html

# Inventory of examiners

This list is current as of september 2021

## Generic

* `ansi_tape_labels - ANSI tape header/trailer records

* `ascii` - ASCII text files, with or without parity

* `bigdigits` - 5x7 fonts - often punched into paper tape

* `bitdata` - Base-class for dealing with bit-aligned data

* `hexdump` - Sometimes that's all you can do

* `iso8632_gcm` - ISO 8632-3 Computer Graphics Metafiles

* `pyreveng3` - Calls on https://github.com/bsdphk/PyReveng3 for disassembly

* `samesame` - summarizes artifacts with a single byte value
  so they dont pointlessly generate a lot of hexdump

* `sccs_id` - `@(#)` "what" markers from sccs(1)

* `tap_file` - SIMH magtape files

* `textfiles` - Recognize specific types of ASCII files, presently only Postscript.

## Data General

* `absbin` - Absolute Binary Format

* `relbin` - Relative Binary Format

* `papertapechecksum` - Product identification marker on paper tapes

## UNIX

* `cbm900_ar` - Commodore CBM 900 ar(1) files

* `cbm900_l_out` - Commodore CBM 900 l_out(4) files

* `cbm900_partition` - Commodore CBM 900 disk partitioning

* `compress` - compress(1) (bla.Z) files

* `fast_filesystem` - Kirk McKusick's BSD4 FFS

* `hpux_disklabel` - HPUX disk partitioning

* `sunos_disklabel` - SunOS 4 etc.

* `sysv_filesystem` - AT&T System V filesystem

* `tar_file` - tar(1) archives

* `unix_fs` - Filesystem base-class

* `v7_filesystem` - As Ken wrote it

* `xenix286_fs` - How SCO botched it

* `xenix286_partition` - As found on the PC platform

## RegneCentralen

* `gier_text` - GIER text files

* `domus_fs` - DOMUS filesystem

* `rc3600_fdtape` - 8" Floppies emulating ½" tapes

* `rc7000_comal` - COMAL save files

* `rc8000_save_tape` - SAVE tapes from RC8000

* `rcsl` - RCSL markers

## Dansk Data Elektronik

* `subdisk2` - Disk Partitioning

* `gks` - Graphical Kernel System

## Rational R1000/s400

* `dfs_tape.py`	- DFS tape files

* `disk_part.py` - Disk partitioning

* `index_data.py` - Archive filesets

* `r1k_6zero.py` - Very often ASCII files

* `r1k_97seg.py` - Possibly DIANA trees

* `r1k_a6seg.py` - Environment WORLDs

* `r1k_assy.py` - Code segments

* `r1k_backup.py` - Backup tape, tape aspects

* `r1k_backup_objects.py` - Backup tape, object aspects

* `r1k_bittools.py` - R1K specific bit tools

* `r1k_diag.py` - DIAG processor firmware disassembly

* `r1k_disass.py` - Call out to https://github.com/Datamuseum-DK/R1000.Disassembly

* `r1k_e3_objects.py` - Ada program editor objects

* `r1k_experiment.py` - Diagnostic experiment DFS files

* `r1k_linkpack.py` - LinkPack object

* `r1k_m200.py` - DFS executables

* `r1k_seg_heap.py` - Baseclass for heap segments

* `r1k_ucode.py` - Microcode DFS files

* `tape_blocks.py` - R1K logical tape blocks

## DDHF specific

* `bitstore` - Get artifacts from the bitarchive

* `decorated_context` - Standard HTML decoration

/phk
