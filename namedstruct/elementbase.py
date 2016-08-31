"""NamedStruct element class."""

import struct
import re

from namedstruct.element import Element
from namedstruct.modes import Mode


class ElementBase(Element):
    """
    The basic NamedStruct element class.
    """

    def __init__(self, field, mode=Mode.Native):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]

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

        Basic elements don't support numeric modifiers, since that requires a
        list of values.
        """
        return len(field) == 2 \
            and isinstance(field[1], str) \
            and re.match(r'[?nNfdP]', field[1])

    def changemode(self, mode):
        """change the mode of the struct format"""
        self._mode = mode
        self.format = mode.value + self.format[1:]
        # recreate the struct with the new format
        self._struct = struct.Struct(self.format)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        return self._struct.pack(msg[self.name])

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        ret = self._struct.unpack_from(buf, 0)
        unused = buf[struct.calcsize(self.format):]
        return (ret[0], unused)

    def make(self, msg):
        """Return the "transformed" value for this element"""
        return msg[self.name]
