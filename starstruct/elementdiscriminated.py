"""StarStruct element class."""

import starstruct
from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementDiscriminated(Element):
    """
    The discriminated StarStruct element class.
    """

    def __init__(self, field, mode=Mode.Native, alignment=1):
        """Initialize a StarStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

        # Discriminated elements don't use the normal struct format, the format
        # is the supplied dictionary where the key is a value of the referenced
        # enum element, and the value for each entry is a StarStruct.Message
        # object.
        self.format = field[1]

        # but change the mode to match the current mode.
        self.update(mode, alignment)

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
            and all(isinstance(val, (starstruct.message.Message, type(None)))
                    for val in field[1].values())

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All Discriminated elements must reference valid Enum elements, and the
        keys of the discriminated format must be valid instances of the
        referenced Enum class.
        """
        from starstruct.elementenum import ElementEnum
        if not isinstance(msg[self.ref], ElementEnum):
            err = 'discriminated field {} reference {} invalid type'
            raise TypeError(err.format(self.name, self.ref))
        elif not all(isinstance(key, msg[self.ref].ref)
                     for key in self.format.keys()):
            err = 'discriminated field {} reference {} mismatch'
            raise TypeError(err.format(self.name, self.ref))
        else:
            for key in self.format.keys():
                try:
                    ref_cls = msg[self.ref].ref
                    assert ref_cls(key)
                except:
                    err = 'discriminated field {} key {} not a valid {}'
                    msg = err.format(self.name, key, self.ref)
                    raise TypeError(msg)

    def update(self, mode=None, alignment=None):
        """change the mode of each message format"""
        self._mode = mode
        self._alignment = alignment

        for key in self.format.keys():
            if self.format[key] is not None:
                self.format[key].update(mode, alignment)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the value of the referenced element to determine
        # which field format to use to pack this element.  Be sure to check if
        # the referenced format is None or a Message object.
        if msg[self.ref] not in self.format:
            msg = 'invalid value {} for element {}:{}'.format(
                msg[self.ref], self.name, self.format.keys())
            raise ValueError(msg)

        if self.format[msg[self.ref]] is not None:
            if msg[self.name] is not None:
                data = self.format[msg[self.ref]].pack(dict(msg[self.name]))
            else:
                data = self.format[msg[self.ref]].pack({})
        else:
            data = b''

        # There is no need to make sure that the packed data is properly
        # aligned, because that should already be done by the individual
        # messages that have been packed.
        return data

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a discriminated element, reference the already unpacked
        # enum field to determine how many elements need unpacked.  If the
        # specific value is None rather than a Message object, return no new
        # parsed data.
        #
        # There is no need to make sure that the unpacked data consumes a
        # properly aligned number of bytes because that should already be done
        # by the message that is unpacked.
        #
        # Use the getattr() function since the referenced value is an enum
        if self.format[getattr(msg, self.ref)] is not None:
            return self.format[getattr(msg, self.ref)].unpack_partial(buf)
        else:
            return (None, buf)

    def make(self, msg):
        """Return the expected "made" value"""
        if hasattr(msg, self.ref):
            key = getattr(msg, self.ref)
        else:
            # Assume it's a dictionary, not a tuple
            key = msg[self.ref]

        if self.format[key] is not None:
            return self.format[key].make(msg[self.name])
        else:
            return None
