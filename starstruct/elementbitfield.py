"""StarStruct element class."""

import struct
import re

from starstruct.element import register, Element
from starstruct.modes import Mode
from starstruct.bitfield import BitField
from starstruct.packedbitfield import PackedBitField


@register
class ElementBitField(Element):
    """
    The bitfield StarStruct element class.
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

        Signed fields are not allowed, bit manipulation does not work well
        """
        return (len(field) == 3 and
                isinstance(field[1], str) and
                re.match(r'\d*[BHILQN]', field[1]) and
                isinstance(field[2], (BitField, PackedBitField)))

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
        # Turn the enum value list into a single number and pack it into the
        # specified format
        data = self._struct.pack(self.ref.pack(msg[self.name]))

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

        # Convert the returned value to the referenced BitField type
        try:
            member = self.ref.unpack(ret[0])
        except ValueError as e:
            raise ValueError(
                'Value: {0} was not valid for {1}\n\twith msg: {2},\n\tbuf: {3}'.format(
                    ret[0], self.ref, msg, buf
                )).with_traceback(e.__traceback__)

        return (member, unused)

    def make(self, msg):
        """Return the "transformed" value for this element"""
        return self.ref.make(msg[self.name])
