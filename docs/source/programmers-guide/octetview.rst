OctetView - A tutorial
======================

OctetView is by far the easiest way to take artifacts apart.

The basic idea is that that artifact is cut into non-overlapping
objects, each of which covers one or more octets in the artifact.

…and then the OctetView class more or less takes care of the rest.

The objects can be examined before they are and discarded or inserted
into the interpretation of the artifact.

Lets take an example:

.. code-block:: none

    from autoarchaeologist.base import octetview as ov
    
    class CBM900LOut(ov.OctetView):
    
        ''' CBM900 L.out binary format '''
    
        def __init__(self, this):
            super().__init__(this)
            header = LdHeader(self, 0)
            if header.l_magic.val != 0o407 or header.l_flag.val != 0x10:
                return
            header.insert()
            self.add_interpretation()

We are writing an examiner for the CBM900 "l.out" object file format,
but first we have to find out if the artifact is one.

After we have initialized the OctetView parent class, we create an
object starting at the first octet in the artifact.

The l.out files start out with this structure:

.. code-block:: none

    struct ldheader {
	int	l_magic;	/* Magic number */
	int	l_flag;		/* Flags */
	int	l_machine;	/* Type of target machine */
	vaddr_t	l_entry;	/* Entrypoint */
	size_t	l_ssize[NLSEG];	/* Segment sizes */
    };

But our view is the actual storage layout of the structure, on this
particular hardware, using that specific C-compiler, so we define
our ``LdHeader`` class like this:

.. code-block:: none

    class LdHeader(ov.Struct):
    
        def __init__(self, tree, lo):
            super().__init__(
                tree,
                lo,
                l_magic_=ov.Le16,
                l_flag_=ov.Le16,
                l_machine_=ov.Le16,
                l_entry_=ov.Le32,
                l_ssize_=ov.Array(9, ov.Le32, vertical=True),
                pad__=2,
                vertical=True,
            )

``tree`` is the OctetView we are working in, aka ``self`` in
the ``CBM900LOut`` class.

``lo`` is the address where this data structure lives.

The name of the next five arguments end in an underscore, so
they each define a field in the structure, by specifying which
class to instantiate for that field.

These classes should be subclassed from ``ov.Octets`` which
``ov.Struct`` also is, so yes:  Fields can be structs too.

OctetView comes with a lot of handy subclasses already,
such as ``ov.Le16`` which is a little-endian 16 bit number.

``ov.Array`` is a factory which will return a class which
implements an array of 9 little-endian 32 bit numbers.

If we run the snippet above we get an interpretation which looks
like this:

.. code-block:: none

    0x000…030 LdHeader {
    0x000…030   l_magic = 0x0107	// @0x0
    0x000…030   l_flag = 0x0010	// @0x2
    0x000…030   l_machine = 0x0004	// @0x4
    0x000…030   l_entry = 0x00000030	// @0x6
    0x000…030   l_ssize = [	// @0xa
    0x000…030       [0x0]: 0x000000be
    0x000…030       [0x1]: 0x00000000
    0x000…030       [0x2]: 0x00000000
    0x000…030       [0x3]: 0x00000000
    0x000…030       [0x4]: 0x00000000
    0x000…030       [0x5]: 0x00000000
    0x000…030       [0x6]: 0x00000000
    0x000…030       [0x7]: 0x0000009a
    0x000…030       [0x8]: 0x0000004e
    0x000…030   ]
    0x000…030 }
    0x030…0ee   ab f1 2f […] 00 a9 fb   ┆  /[…]   ┆
    […]

The rest of the artifact is hexdumped, because we have not
created any objects to cover that part of it.

The ``pad__=2`` field is missing because field arguments
which end in two underscores are not rendered.

If we had not specified ``vertical=True`` to ``ov.Array``
the members of the array would all be on a single line,
and likewise, without ``vertical=True`` the entire ``LdHeader``
would be rendered on a single line.

Having structures and arrays horizontal while a data format is
reverse engineered makes it possible to ``grep -r`` all instances
of a struct in the entire excavation, to try to glean what this or
that field can contain and might mean.

We can also handle variable structures:

.. code-block:: none

    class Something(ov.Struct):
    
        def __init__(self, tree, lo):
            super().__init__(
                tree,
                lo,
                width_=ov.Be24,
                name_=ov.Text(5),
                more=True,
            )
            if self.width.val < (1<<8):
                self.add_field("payload", ov.Octet)
            elif self.width.val < (1<<16):
                self.add_field("payload", ov.Be16)
            elif self.width.val < (1<<24):
                self.add_field("payload", ov.Be24)
            else:
                print("Somethings wrong", self)
                exit(2)
            self.done()

``ov.Text`` is a factory which returns a class for a string of
a given length.

These classes have a ``render()`` method which is responsible for
how they will appear in the interpretation, so for instance a RC4000
timestamp can be defined like this:

.. code-block:: none

    class ShortClock(ov.Be24):
    
        def render(self):
            if self.val == 0:
                yield "                "
            else:
                ut = (word << 19) * 100e-6
                t0 = (366+365)*24*60*60
                yield time.strftime(
                    "%Y-%m-%dT%H:%M",
                    time.gmtime(ut - t0)
                )

And finally:

If bytes are too big the the job, ``OctetView`` has a sibling called
``BitView``, which can do the exact same things, but with 8 times
higher resolution.  Unfortunately, it is much more than 8 times
slower - but when you need bits, you need bits.

