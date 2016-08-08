"""NamedStruct element class."""

import namedstruct
from namedstruct.element import Element


class ElementVariable(Element):
    """
    The variable NamedStruct element class.
    """

    # pylint: disable=unused-argument
    def __init__(self, field, mode):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

        # Variable elements don't use the normal struct format, the format is
        # a NamedStruct.Message object.
        self.format = field[1]

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
            and isinstance(field[2], str)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the length of the current element to determine
        # how many elements to pack, not the length element of the message
        # (which should not be specified manually).
        ret = [self.format.pack(dict(elem)) for elem in msg[self.name]]
        return b''.join(ret)

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a variable element, reference the already unpacked
        # length field to determine how many elements need unpacked.
        ret = []
        unused = buf
        for i in range(getattr(msg, self.ref)):  # pylint: disable=unused-variable
            (val, unused) = self.format.unpack(unused)
            ret.append(val)
        return (ret, unused)
