"""Package for NamedStruct."""

import sys

__project__ = 'NamedStruct'
__version__ = '0.9.0'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 5

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    # pylint: disable=wrong-import-position
    from namedstruct.message import Message
    from namedstruct.modes import Mode

    # silence F401 flake8 error
    assert Message
    assert Mode

    __all__ = ['Message', 'Mode']
except ImportError:  # pragma: no cover (manual test)
    pass
