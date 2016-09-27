"""NamedStruct element class."""

import struct

import namedstruct
from namedstruct.element import Element


class ElementVariable(Element):
    """
    The variable NamedStruct element class.

    Can be used in two ways:

    message_struct = [
        ('length', 'H', 'vardata'),            # unsigned short length field
        ('vardata',                            # variable length data
         Message('VarTest', [('x', 'B'), ('y', 'B')]),
         'length'),
    ]

    Note that length is the string and you can think of it as "linking" to the
    length that is provided in the length field.


    message_struct = [
        ('repeated_data',
         Message('Repeated', [('x', 'B'), ('y', 'H')]),
         3),
    ]

    Now we provide an integer that tells us that there will ALWAYS be that many
    messages in this message. You also no longer need to have another field
    that specifies the number of these messages.
    """

    # pylint: disable=unused-argument
    def __init__(self, field, mode):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

        # Variable elements don't use the normal struct format, the format is
        # a NamedStruct.Message object, but change the mode to match the
        # current mode.
        self.format = field[1]
        # Set the packing style for the struct
        if isinstance(self.ref, str):
            self.variable_repeat = True
        else:
            self.variable_repeat = False

        self.changemode(mode)

    @staticmethod
    def valid(field):
        """
        Validation function to determine if a field tuple represents a valid
        enum element type.

        The basics have already been validated by the Element factory class,
        validate that the struct format is a valid numeric value.
        """
        return len(field) == 3 \
            and isinstance(field[1], namedstruct.message.Message) \
            and isinstance(field[2], (str, int))

    def changemode(self, mode):
        """change the mode of the message format"""
        self._mode = mode
        self.format.changemode(mode)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the length of the current element to determine
        # how many elements to pack, not the length element of the message
        # (which should not be specified manually).
        if self.variable_repeat:
            ret = [self.format.pack(dict(elem)) if elem else self.format.pack({})
                   for elem in msg[self.name]]
        else:
            empty_byte = struct.pack('x')
            ret = [self.format.pack(msg[self.name][index]) if index < len(msg[self.name]) else empty_byte * len(self.format)
                   for index in range(self.ref)]

        return b''.join(ret)

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a variable element, reference the already unpacked
        # length field to determine how many elements need unpacked.
        ret = []
        unused = buf
        for i in range(getattr(msg, self.ref)):  # pylint: disable=unused-variable
            (val, unused) = self.format.unpack_partial(unused)
            ret.append(val)
        return (ret, unused)

    def make(self, msg):
        """Return the expected "made" value"""
        ret = []
        for val in msg[self.name]:
            ret.append(self.format.make(val))
        return ret
