"""StarStruct element class."""
# pylint: disable=line-too-long

import struct

import starstruct
from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementVariable(Element):
    """
    The variable StarStruct element class.
    Can be used in multiple ways ways:

    1) ------------------------------------------------------------------------
    Variable Lengths, in terms of starstruct elements

    NOTE: The length item is specified as a string, not as bytes

    ExampleMessage = Message('VarTest', [('x', 'B'), ('y', 'B')])

    message_struct = [
        ('length_in_objects', 'H', 'vardata'),            # length field
        ('vardata', ExampleMessage, 'length_in_objects')  # variable length data
    ]

    Note that length is the string and you can think of it as "linking" to the
    length that is provided in the length field.

    2) ------------------------------------------------------------------------
    Variable lengths, in terms of byte size

    NOTE: The length item is specified as bytes, not as a string

    SomeMessage = starstruct.Message(...)

    message_struct = [
        (b'length_in_bytes', 'B', 'vardata'),
        ('vardata', SomeMessage, b'length_in_bytes'),
    ]

    Now if our program specifies taht we should have a length in bytes field
    we can say 'length_in_bytes' = 8, while only have 2 SomeMessage, (assuming
    that the length of SomeMessge == 4).

    3) ------------------------------------------------------------------------
    Fixed length, in terms of starstruct elements

    RepeatedMessage = Message('Repeated', [('x', 'B'), ('y', 'H')])

    message_struct = [
        ('repeated_data', RepeatedMessage, 3),
    ]

    Now we provide an integer that tells us that there will ALWAYS be that
    many messages in this message. You also no longer need to have another
    field that specifies the number of these messages.

    4) ------------------------------------------------------------------------
    TODO: Fixed length, in terms of bytes?

    Might have something that can only fit a certain number of bytes, like a
    CAN message, and this would break it up automatically?

    """

    def __init__(self, field, mode=Mode.Native, alignment=1):
        """Initialize a StarStruct element object."""

        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]
        self.ref = field[2]

        # Variable elements don't use the normal struct format, the format is
        # a StarStruct.Message object, but change the mode to match the
        # current mode.
        self.format = field[1]

        # Set the packing style for the struct
        if isinstance(self.ref, (str, bytes)):
            self.variable_repeat = True

            # Determine whether bytes or objects are the measurement tool
            if isinstance(self.ref, str):
                self.object_length = True
            else:
                self.object_length = False

                # Change our ref to be a string, for NamedTuple
                self.ref = self.ref.decode('utf-8')
        else:
            self.variable_repeat = False

            # TODO: If we add #4, then we would have to have a check here
            self.object_length = True

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
            and isinstance(field[1], starstruct.message.Message) \
            and isinstance(field[2], (str, int, bytes))

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All elements that are Variable must reference valid Length elements.
        """
        from starstruct.elementlength import ElementLength
        if self.variable_repeat:
            # Handle object length, not byte length
            if self.object_length:
                if not isinstance(msg[self.ref], ElementLength):
                    err = 'variable field {} reference {} invalid type'
                    raise TypeError(err.format(self.name, self.ref))
                elif not msg[self.ref].ref == self.name:
                    err = 'variable field {} reference {} mismatch'
                    raise TypeError(err.format(self.name, self.ref))
            # Handle byte length, not object length
            else:
                # TODO: Validate the object
                pass
        else:
            if not isinstance(self.ref, int):
                err = 'fixed repetition field {} reference {} not an integer'
                raise TypeError(err.format(self.name, self.ref))

    def update(self, mode=None, alignment=None):
        """change the mode of the struct format"""
        self._mode = mode
        self._alignment = alignment
        self.format.update(mode, alignment)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the length of the current element to determine
        # how many elements to pack, not the length element of the message
        # (which should not be specified manually).
        if self.variable_repeat:
            if self.object_length:
                ret = [self.format.pack(dict(elem)) if elem else self.format.pack({})
                       for elem in msg[self.name]]
            else:
                ret = []
                length = 0

                for elem in msg[self.name]:
                    temp_elem = self.format.pack(dict(elem))

                    if length + len(temp_elem) <= msg[self.ref]:
                        ret.append(temp_elem)

        # Pack as many bytes as we have been given
        # and fill the rest of the byets with empty packing
        else:
            empty_byte = struct.pack('x')
            ret = [self.format.pack(msg[self.name][index]) if index < len(msg[self.name]) else empty_byte * len(self.format)
                   for index in range(self.ref)]

        # There is no need to make sure that the packed data is properly
        # aligned, because that should already be done by the individual
        # messages that have been packed.
        return b''.join(ret)

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a variable element, reference the already unpacked
        # length field to determine how many elements need unpacked.
        ret = []
        unused = buf
        if self.object_length:
            for _ in range(getattr(msg, self.ref)):
                (val, unused) = self.format.unpack_partial(unused)
                ret.append(val)
        else:
            length = 0
            while length < getattr(msg, self.ref):
                (val, unused) = self.format.unpack_partial(unused)
                length += len(val)
                ret.append(val)

        # There is no need to make sure that the unpacked data consumes a
        # properly aligned number of bytes because that should already be done
        # by the individual messages that have been unpacked.
        return (ret, unused)

    def make(self, msg):
        """Return the expected "made" value"""
        ret = []
        for val in msg[self.name]:
            ret.append(self.format.make(val))
        return ret
