"""StarStruct element class."""

import struct
import re

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementString(Element):
    """
    A StarStruct element for strings, because standard string treatment of
    pack/unpack can be inconvenient.

    This element will encode and decode string type elements from and to forms
    that are easier to use and manage.
    """

    def __init__(self, field, mode=Mode.Native, alignment=1):
        """Initialize a StarStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]

        # The ref attribute is required for all elements, but base element
        # types don't have one
        self.ref = None

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
        string element type.
        """
        return len(field) == 2 \
            and isinstance(field[1], str) \
            and re.match(r'\d*[csp]', field[1])

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        The "string" element requires no further validation.
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
        # Ensure that the input is of the proper form to be packed
        val = msg[self.name]
        size = struct.calcsize(self.format)
        assert len(val) <= size
        if self.format[-1] in ('s', 'p'):
            if not isinstance(val, bytes):
                assert isinstance(val, str)
                val = val.encode()
                if self.format[-1] == 'p' and len(val) < size:
                    # 'p' (pascal strings) must be the exact size of the format
                    val += b'\x00' * (size - len(val))
            data = self._struct.pack(val)
        else:  # 'c'
            if not all(isinstance(c, bytes) for c in val):
                if isinstance(val, bytes):
                    val = [bytes([c]) for c in val]
                else:
                    # last option, it could be a string, or a list of strings
                    assert (isinstance(val, list) and
                            all(isinstance(c, str) for c in val)) or \
                        isinstance(val, str)
                    val = [c.encode() for c in val]
            if len(val) < size:
                val.extend([b'\x00'] * (size - len(val)))
            data = self._struct.pack(*val)

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

        val = ret[0]
        if self.format[-1] in 's':
            # for 's' formats, convert to a string and strip padding
            val = val.decode().strip('\x00')
        elif self.format[-1] in 'p':
            # for 'p' formats, convert to a string, but leave the padding
            val = val.decode()
        else:  # 'c'
            val = [c.decode() for c in val]
        return (val, unused)

    def make(self, msg):
        """Return a string of the expected format"""
        val = msg[self.name]
        size = struct.calcsize(self.format)
        assert len(val) <= size

        # If the supplied value is a list of chars, or a list of bytes, turn
        # it into a string for ease of processing.
        if isinstance(val, list):
            if all(isinstance(c, bytes) for c in val):
                val = ''.join([c.decode() for c in val])
            elif all(isinstance(c, str) for c in val):
                val = ''.join([c for c in val])
            else:
                error = 'Invalid value for string element: {}'
                raise TypeError(error.format(val))
        elif isinstance(val, bytes):
            # If the supplied value is a byes, decode it into a normal string
            val = val.decode()

        # 'p' (pascal strings) and 'c' (char list) must be the exact size of
        # the format
        if self.format[-1] in ('p', 'c') and len(val) < size:
            val += '\x00' * (size - len(val))

        # Lastly, 'c' (char list) formats are expected to be a list of
        # characters rather than a string.
        if self.format[-1] == 'c':
            val = [c for c in val]

        return val
