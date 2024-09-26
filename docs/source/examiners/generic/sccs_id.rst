
SCCS Id strings
===============

This examiner looks for what(1) strings, and add any it finds to
the artifact as a note.

What(1) strings start with "@(#)" and ends at the first newline,
double quote, '>' or backslash.

A typical example is:

.. code-block:: none

	@(#) addbfcrc.c 1.5 89/03/08 14:58:35 

These strings were a feature of the original sccs(1) version control
program on UNIX, and it makes it possible to automatically include
information about source code version(s) into program files, which the
what(1) program can then extract again.
