"""NamedStruct element class."""

import struct
import re
import enum

from namedstruct.element import Element
from namedstruct.modes import Mode


class ElementNum(Element):
    """
    A NamedStruct element class for number fields.
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

        # for numeric elements we should also keep track of how many numeric
        # fields and what the size of those fields are required to create this
        # element.
        self._bytes = struct.calcsize(self.format[-1])
        self._signed = self.format[-1] in 'bhilq'

    @staticmethod
    def valid(field):
        """
        Validation function to determine if a field tuple represents a valid
        base element type.

        The basics have already been validated by the Element factory class,
        validate the specific struct format now.
        """
        return len(field) == 2 \
            and isinstance(field[1], str) \
            and re.match(r'\d*[bBhHiIlLqQ]', field[1])

    def changemode(self, mode):
        """change the mode of the struct format"""
        self._mode = mode
        self.format = mode.value + self.format[1:]
        # recreate the struct with the new format
        self._struct = struct.Struct(self.format)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # Take a single numeric value and convert it into the necessary list
        # of values required by the specified format.
        val = msg[self.name]

        # This should be a number, but handle cases where it's an enum
        if isinstance(val, enum.Enum):
            val = val.value

        # If the value supplied is not already a bytes object, convert it now.
        if isinstance(val, bytes):
            val_list = val
        else:
            val_list = val.to_bytes(struct.calcsize(self.format),
                                    byteorder=self._mode.to_byteorder(),
                                    signed=self._signed)

        # join the byte list into the expected number of values to pack the
        # specified struct format.
        val = [int.from_bytes(val_list[i:i + self._bytes],  # pylint: disable=no-member
                              byteorder=self._mode.to_byteorder(),
                              signed=self._signed)
               for i in range(0, len(val_list), self._bytes)]
        return self._struct.pack(*val)

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        ret = self._struct.unpack_from(buf, 0)
        unused = buf[struct.calcsize(self.format):]
        # merge the unpacked data into a byte array
        data = [v.to_bytes(self._bytes, byteorder=self._mode.to_byteorder(),
                           signed=self._signed) for v in ret]
        # Join the returned list of numbers into a single value
        val = int.from_bytes(b''.join(data),  # pylint: disable=no-member
                             byteorder=self._mode.to_byteorder(),
                             signed=self._signed)
        return (val, unused)

    def make(self, msg):
        """Return the expected "made" value"""
        val = msg[self.name]

        # This should be a number, but handle cases where it's an enum
        if isinstance(val, enum.Enum):
            val = val.value
        elif isinstance(val, list):
            # It's unlikely but possible that this could be a list of numbers,
            # or a list of bytes
            if all(isinstance(v, bytes) for v in val):
                # To turn this into a single number, merge the bytes, later the
                # bytes will be converted into a single number.
                data = b''.join(val)
            elif all(isinstance(v, int) for v in val):
                # To turn this into a single number, convert the numbers into
                # bytes, and merge the bytes, later the bytes will be converted
                # into a single number.
                data = [v.to_bytes(self._bytes,
                                   byteorder=self._mode.to_byteorder(),
                                   signed=self._signed) for v in val]
            else:
                error = 'Invalid value for numerical element: {}'
                raise TypeError(error.format(val))
        elif isinstance(val, bytes):
            # If the value supplied is a bytes object, convert it to a number
            data = val
        elif isinstance(val, int):
            return val
        else:
            error = 'Invalid value for numerical element: {}'
            raise TypeError(error.format(val))

        return int.from_bytes(data,  # pylint: disable=no-member
                              byteorder=self._mode.to_byteorder(),
                              signed=self._signed)
