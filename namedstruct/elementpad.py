"""NamedStruct element class."""

import struct
import re

from namedstruct.element import Element
from namedstruct.modes import Mode


class ElementPad(Element):
    """
    The basic NamedStruct element class.
    """

    def __init__(self, field, mode=Mode.Native):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory

        # Pad elements effectively have no name
        self.name = None

        # The ref attribute is required for all elements, but the base element
        # type does not have one
        self.ref = None

        # Validate that the format specifiers are valid struct formats, this
        # doesn't have to be done now because the format will be checked when
        # any struct functions are called, but it's better to inform the user of
        # any errors earlier.
        # The easiest way to perform this check is to create a "Struct" class
        # instance, this will also increase the efficiency of all struct related
        # functions called.
        self._mode = mode
        self.format = mode.value + field[1]
        self._struct = struct.Struct(self.format)

    @staticmethod
    def valid(field):
        """
        Validation function to determine if a field tuple represents a valid
        base element type.

        The basics have already been validated by the Element factory class,
        validate the specific struct format now.
        """
        return len(field) == 2 \
            and re.match(r'\d*x', field[1])

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        return self._struct.pack()

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        unused = buf[struct.calcsize(self.format):]
        return (None, unused)
