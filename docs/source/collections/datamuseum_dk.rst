
Datamusem.dk
~~~~~~~~~~~~

Datamuseum.dk has thousands of digital artifacts in their bitstore:

https://datamuseum.dk/wiki/Bits:Keyword

Example:

.. code-block:: none

    from autoarchaeologist import Excavation
    
    from autoarchaeologist.collection import datamuseum_dk
    
    class DdhfCbm900(Excavation):
    
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
    
            […]
    
            datamuseum_dk.FromBitStore(
                self,
                "-30001199",
                "CBM900",
            )

The arguments can be either item numbers or keywords, and if prefixed
with a minus they will be excluded, even if subsequent arguments
match them.
