Data model
==========

It is important to understand the overall data model if you want
to work in, and to a lesser degree with, the Autoarchaeologist.

Unless otherwise noted, all these are python classes, which can
be freely subclassed.

Excavation
----------

An excavation is the top level data structure which turns a number
of input files into a number of HTML files.

* Drives the process of examination
* Drives the production of HTML output files
* Provide default interpretation of unloved artifacts
* Can decorate the HTML output files
* Provides the default values and parameters
* Creates the artifacts
* Provides various services to everything else

Relationships:

* Holds the artifacts (top- and excavated-)
* Holds the examiners
* Holds the default typecase
* Offers each artifact to each examiner once.

Artifact
--------

An artifact is a collection of one or more octets.

* Has a single unique sequential ordering of its octets
* Has a unique identifier (SHA256 of the unique sequential ordering)
* May be a concatenation of records
* May be a top-level artifact (= The files provided as input)

Relationships:

* May have notes
* May have types
* May have namespaces
* May have interpretations
* May have child artifacts
* May have a typecase (otherwise it will inherit one)

Record
------

A record is a fragment of an artifact.

* Has a key which is either None or a tuple
* Contains at least one octet

Relationships:

* Keys do not control the order of records in the artifact
* By convention disk-like artifacts use (cyl, head, sect) keys.
* By convention tape-like artifacts use (file, block) keys.

Examiner
--------

Tries to understand and interpret (some of) the artifacts, with
increasingly expensive checks to determine if it is an artifact
it can analyse, and then a full analysis.

Relationships:

* Is offered each artifact exactly once
* Can attach notes to artifacts
* Can attach types to artifacts
* Can attach namespaces to artifacts
* Can attach HTML or Unicode interpretations to artifacts
* Can, but normally should not, call other Examiners directly

Typecase
--------

Translates a character set into Unicode.

* Can translate a sequence of integers to short or long UTF-8 representation

TODO: Modal character sets like BAUDOT (telex, teleprinter)

Relationships:

* Is basically an array of Glyphs

Glyphs
------

Holds the information about one code point in a character set

* Has a "short" Unicode single-position, representation suitable for (hex)dumps
* Has a "long" Unicode representation which is "does the right thing" (for instance newlines)
* Can have flags (INVALID, IGNORE, EOF and others) which affect interpretation

Containers
----------

Some input artifacts will be raw bytes, for instance a hard disk
image, others will be container formats such as ``.IMD``, ``SIMH-TAP``
and ``ZIP``.

If we wanted to, we could ingest these containers, examine them
with ``OctetView`` and create the artifacts they contain for further
examination.

But our audience is not here to see how ``IMD`` files are constructed,
so it makes more sense to not instantiate the container files directly,
but only what they contain.

This is what ``containers`` do, and some of them even do it with the
``OctetView``, they just dont create an HTML interpretation.

Collections
-----------

AA will be used on artifacts from various public collections, Datamuseum.DK's
own BitArchive, Al Kossow & CHM's bitsavers.org and so on.

The collection classes makes it easier to pull in artifacts from
such well known collections, and cache the downloaded artifacts
to reduce traffic.
