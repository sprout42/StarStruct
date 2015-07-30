"""NamedStruct class."""

import struct
import collections

from namedstruct.modes import Mode


class NamedStruct(object):

    """An object much like NamedTuple, but with additional formatting."""

    def __init__(self, name, fields, mode=Mode.Native):
        """
        Initialize a NamedStruct object.

        Creates 2 internal items, a format string which is used to call the
        struct module functions for packing and unpacking data, and a
        namedtuple instance which is used to organize the data provided to the
        pack functions and returned from the unpack functions.
        """

        # The name must be a string, this is provided to the
        # collections.namedtuple constructor when creating the namedtuple class.
        if not name or not isinstance(name, str):
            raise TypeError('invalid name: {}'.format(name))

        # The structure definition must be a list of ('field', 'pad') string
        # tuples
        if not isinstance(fields, list) \
                or not all(isinstance(x, tuple) for x in fields):
            raise TypeError('invalid fields: {}'.format(fields))

        if not isinstance(mode, Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        fmt = mode.value + ''.join([x[1] for x in fields])

        # Validate that the format specifiers are valid struct formats, this
        # doesn't have to be done now because the format will be checked when
        # any struct functions are called, but it's better to inform the user of
        # any errors earlier.
        # The easiest way to perform this check is to create a "Struct" class 
        # instance, this will also increase the efficiency of all struct related 
        # functions called.
        self._struct = struct.Struct(fmt)

        # Make a list of fields to place into the named tuple leaving out any
        # fields that have an encoding of '*x'
        fields = [x[0] for x in fields if x[1][-1] != 'x']
        self._tuple = collections.namedtuple(name, fields)

    def pack(self, **kwargs):
        """Pack the provided values using the initialized format."""

        return self._struct.pack(*self._tuple(**kwargs))

    def pack_into(self, buf, offset, **kwargs):
        """Pack the provided values into the supplied buffer."""

        return self._struct.pack_into(buf, offset, *self._tuple(**kwargs))

    def unpack(self, buf):
        """Unpack the buffer using the initialized format."""

        return self._tuple(*self._struct.unpack(buf))

    def unpack_from(self, buf, offset=0):
        """Unpack data from the supplied buffer using the initialized format."""

        return self._tuple(*self._struct.unpack_from(buf, offset))

    def size(self):
        """Calculate the space required by the initialized format."""

        return self._struct.size
