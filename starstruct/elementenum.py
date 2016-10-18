"""StarStruct element class."""

import struct
import re
import enum

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementEnum(Element):
    """
    The enumeration StarStruct element class.
    """

    def __init__(self, field, mode=Mode.Native, alignment=1):
        """Initialize a StarStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
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
        validate that the struct format is a valid numeric value.
        """
        return (len(field) == 3 and
                isinstance(field[1], str) and
                re.match(r'[cbB?hHiIlLqQnNfdP]|\d*[sp]', field[1]) and
                issubclass(field[2], enum.Enum))

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        The "enum" element requires no further validation.
        """
        pass

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
        # The value to pack could be a raw value, or an enum value, first
        # ensure that the value provided is a valid value for the referenced
        # enum class.
        enum_val = self.ref(msg[self.name])
        data = self._struct.pack(enum_val.value)

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

        # Convert the returned value to the referenced Enum type
        return (self.ref(ret[0]), unused)

    def make(self, msg):
        """Return the "transformed" value for this element"""
        return self.ref(msg[self.name])
