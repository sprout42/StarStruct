"""Package for NamedStruct."""

import sys

__project__ = 'NamedStruct'
__version__ = '0.1.0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 4

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    from namedstruct.struct import NamedStruct
    from namedstruct.modes import Mode
except ImportError:  # pragma: no cover (manual test)
    pass
