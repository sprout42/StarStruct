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
        self._mode = mode
        self.format = field[1]

        # but change the mode to match the current mode.
        for key in self.format.keys():
            if self.format[key]:
                self.format[key].changemode(mode)

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
            and all(isinstance(val, (namedstruct.message.Message, type(None)))
                    for val in field[1].values())

    def changemode(self, mode):
        """change the mode of each message format"""
        self._mode = mode
        for key in self.format.keys():
            if self.format[key]:
                self.format[key].changemode(mode)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the value of the referenced element to determine
        # which field format to use to pack this element.  Be sure to check if
        # the referenced format is None or a Message object.
        if msg[self.ref] not in self.format:
            msg = 'invalid value {} for element {}:{}'.format(
                msg[self.ref], self.name, self.format.keys())
            raise ValueError(msg)

        if self.format[msg[self.ref]]:
            if msg[self.name]:
                return self.format[msg[self.ref]].pack(dict(msg[self.name]))
            else:
                return self.format[msg[self.ref]].pack({})
        else:
            return b''

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a discriminated element, reference the already unpacked
        # enum field to determine how many elements need unpacked.  If the
        # specific value is None rather than a Message object, return no new
        # parsed data.
        if self.format[getattr(msg, self.ref)]:
            return self.format[getattr(msg, self.ref)].unpack(buf)
        else:
            return (None, buf)
