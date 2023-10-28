#!/usr/bin/env python3

''' Create an artifact from a plain file '''

import mmap

from ..base import artifact

class PlainFileArtifact(artifact.ArtifactStream):
    ''' Create an artifact from a plain file '''

    def __init__(self, filename):
        with open(filename, 'rb') as file:
            self._mmap = mmap.mmap(
                file.fileno(),
                0,
                access=mmap.ACCESS_READ,
            )
        super().__init__(self._mmap)
