"""Package for StarStruct."""

import importlib
import glob
import os
import sys

__project__ = 'StarStruct'
__version__ = '0.9.1'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 5

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

# Import all the different elements automatically.
# This makes sure than any new elements added are imported into the project
# and registered.
file_path = os.path.dirname(os.path.abspath(__file__))

added_elements = []
for f in glob.glob(file_path + '/element*'):
    import_name = os.path.basename(f)[:-3]
    added_elements.append(importlib.import_module('starstruct.' + import_name))


# To find out which elements have been added, just uncomment this statement
# print(added_elements)

# pylint: disable=wrong-import-position
from starstruct.message import Message
from starstruct.modes import Mode

# silence F401 flake8 error
assert Message
assert Mode

from starstruct.startuple import StarTuple
assert StarTuple

from starstruct.bitfield import BitField
assert BitField

from starstruct.packedbitfield import PackedBitField
assert PackedBitField

__all__ = ['Message', 'Mode', 'StarTuple', 'BitField', 'PackedBitField']
