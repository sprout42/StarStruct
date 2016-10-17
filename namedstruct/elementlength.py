"""StarStruct element class."""

import struct
import re

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementLength(Element):
    """
    The length StarStruct element class.
    """

    def __init__(self, field, mode=Mode.Native, alignment=1):
        """Initialize a StarStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        if isinstance(field[0], str):
            self.name = field[0]
            self.object_length = True
        elif isinstance(field[0], bytes):
            self.name = field[0].decode('utf-8')
            self.object_length = False

        self.ref = field[2]

        self._mode = mode
        self._alignment = alignment

        # Validate that the format specifiers are valid struct formats, this
        # doesn't have to be done now because the format will be checked when
        # any struct functions are called, but it's better to inform the user of
        # any errors earlier.
        # The easiest way to perform this check is to create a "Struct" class
        # instance, this will also increase the efficiency of all struct related
        # functions called.
        self.format = mode.value + field[1]
        self._struct = struct.Struct(self.format)

    @staticmethod
    def valid(field):
        """
        Validation function to determine if a field tuple represents a valid
        enum element type.

        The basics have already been validated by the Element factory class,
        validate that the struct format is a valid unsigned numeric value.
        """
        return len(field) == 3 \
            and isinstance(field[1], str) \
            and re.match(r'[BHILQ]', field[1]) \
            and isinstance(field[2], str) and len(field[2])

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All elements that are Variable must reference valid Length elements.
        """
        # TODO: Allow referencing multiple elements for byte lengths?

        from starstruct.elementvariable import ElementVariable
        if not isinstance(msg[self.ref], ElementVariable):
            err = 'length field {} reference {} invalid type'
            raise TypeError(err.format(self.name, self.ref))
        elif not msg[self.ref].ref == self.name:
            err = 'length field {} reference {} mismatch'
            raise TypeError(err.format(self.name, self.ref))

    def update(self, mode=None, alignment=None):
        """change the mode of the struct format"""
        if alignment:
            self._alignment = alignment

        if mode:
            self._mode = mode
            self.format = mode.value + self.format[1:]
            # recreate the struct with the new format
            self._struct = struct.Struct(self.format)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        if self.object_length:
            # When packing a length element, use the length of the referenced
            # element not the value of the current element in the supplied
            # object.
            data = self._struct.pack(len(msg[self.ref]))
        else:
            # When packing something via byte length,
            # we use our self to determine the length
            data = self._struct.pack(msg[self.name])

        # If the data does not meet the alignment, add some padding
        missing_bytes = len(data) % self._alignment
        if missing_bytes:
            data += b'\x00' * missing_bytes
        return data

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        ret = self._struct.unpack_from(buf, 0)

        # Remember to remove any alignment-based padding
        extra_bytes = self._alignment - 1 - (struct.calcsize(self.format) %
                                             self._alignment)
        unused = buf[struct.calcsize(self.format) + extra_bytes:]
        return (ret[0], unused)

    def make(self, msg):
        """Return the length of the referenced array"""
        if self.object_length:
            return len(msg[self.ref])
        else:
            return msg[self.name]
