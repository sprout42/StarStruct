"""Package for StarStruct."""

import sys

__project__ = 'StarStruct'
__version__ = '0.9.1'

VERSION = __project__ + '-' + __version__

PYTHON_VERSION = 3, 5

if not sys.version_info >= PYTHON_VERSION:  # pragma: no cover (manual test)
    exit("Python {}.{}+ is required.".format(*PYTHON_VERSION))

try:
    # pylint: disable=wrong-import-position
    from starstruct.message import Message
    from starstruct.modes import Mode

    # TODO: make this import more automatic
    from starstruct.element import Element
    from starstruct.elementbase import ElementBase
    from starstruct.elementpad import ElementPad
    from starstruct.elementenum import ElementEnum
    from starstruct.elementnum import ElementNum
    from starstruct.elementfixedpoint import ElementFixedPoint
    from starstruct.elementstring import ElementString
    from starstruct.elementlength import ElementLength
    from starstruct.elementvariable import ElementVariable
    from starstruct.elementdiscriminated import ElementDiscriminated

    # silence F401 flake8 error
    assert Message
    assert Mode
    assert Element
    assert ElementBase
    assert ElementPad
    assert ElementEnum
    assert ElementNum
    assert ElementFixedPoint
    assert ElementString
    assert ElementLength
    assert ElementVariable
    assert ElementDiscriminated

    __all__ = ['Message', 'Mode']
except ImportError:  # pragma: no cover (manual test)
    pass
