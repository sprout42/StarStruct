"""NamedStruct element class."""

import namedstruct
from namedstruct.element import Element


class ElementDiscriminated(Element):
    """
    The discriminated NamedStruct element class.
    """

    # pylint: disable=unused-argument
    def __init__(self, field, mode):
        """Initialize a NamedStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

        # Discriminated elements don't use the normal struct format, the format
        # is the supplied dictionary where the key is a value of the referenced
        # enum element, and the value for each entry is a NamedStruct.Message
        # object.
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
            and isinstance(field[1], dict) \
            and isinstance(field[2], str) \
            and all(isinstance(val, namedstruct.message.Message)
                    for val in field[1].values())

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the value of the referenced element to determine
        # which field format to use to pack this element.
        return self.format[msg[self.ref]].pack(dict(msg[self.name]))

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a discriminated element, reference the already unpacked
        # enum field to determine how many elements need unpacked.
        return self.format[getattr(msg, self.ref)].unpack(buf)
