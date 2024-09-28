
Bitsavers.org
~~~~~~~~~~~~~

Bitsavers.org is the largest public collection of IT history artifacts.

https://bitsavers.org/

This class is very rudimentary and has not been tested beyond this example:

.. code-block:: none

    from autoarchaeologist import Excavation
    
    from autoarchaeologist.collection import bitsavers_org
    
    class BitSaversIbm34(Excavation):
    
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
    
            […]
    
            bitsavers_org.FromBitsavers(
                self,
                "-bits/IBM/System_34/S34_diag_set2",
                "-bits/IBM/System_34/S34_diags",
                "bits/IBM/System_34/",
            )


The arguments can be files or directories.  Arguments prefixed with a
minus are excluded, even if subsequent arguments match them.
