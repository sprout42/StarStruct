"""NamedStruct element class."""

import struct
import re

from namedstruct.element import Element
from namedstruct.modes import Mode


class ElementVariable(Element):
    """
    The variable NamedStruct element class.
    """

    def __init__(self, field, mode=Mode.Native):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

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
        enum element type.

        The basics have already been validated by the Element factory class,
        validate that the struct format is a valid numeric value.
        """
        return len(field) == 3 \
            and re.match(r'\d*[cbBhHiIlLqQ]', field[1]) \
            and isinstance(field[2], str)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the length of the current element to determine
        # how many elements to pack, not the length element of the message
        # (which should not be specified manually).
        return b''.join([self._struct.pack(elem) for elem in msg[self.name]])

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a variable element, reference the already unpacked
        # length field to determine how many elements need unpacked.
        ret = []
        for i in range(msg[self.ref]):
            val = self._struct.unpack_from(buf, i * self._struct.calcsize)
            ret.append(val[0])
        unused = buf[(len(ret) * struct.calcsize(self.format)):]
        return (ret, unused)
