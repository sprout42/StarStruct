"""
The escaped NamedStruct element class.

Can be used in multiple ways ways:

1: Variable Lengths, in terms of namedstruct elements

    .. code-block:: python

        ExampleMessage = Message('VarTest', [('x', 'B'), ('y', 'B')])
        TestStruct = Message('TestStruct', [
            ('escaped_data', ExampleMessage, {
                'escape': {
                    'start': b'\xff\x00\xff\x11',
                    'separator': b'\x12\x34',
                    'end': b'\x11\xff\x00\xff',
                },
            }),
        ])

    `start` is the starting escape sequence
    `separator` is a separating sequence
    `end` is the ending escape sequence

"""
# pylint: disable=line-too-long

from typing import Optional

import starstruct
from starstruct.element import register, Element
from starstruct.modes import Mode


class Escapor:
    def __init__(self, start=None, separator=None, end=None, opts=None):
        self._start = start
        self._separator = separator
        self._end = end

        self._opts = opts

    @property
    def start(self):
        if self._start is not None:
            return self._start
        else:
            return b''

    @property
    def separator(self):
        if self._separator is not None:
            return self._separator
        else:
            return b''

    @property
    def end(self):
        if self._end is not None:
            return self._end
        else:
            return b''


@register
class ElementEscaped(Element):
    """
    Initialize a StarStruct element object.

    :param field: The fields passed into the constructor of the element
    :param mode: The mode in which to pack the bytes
    :param alignment: Number of bytes to align to
    """
    def __init__(self, field: list, mode: Optional[Mode]=Mode.Native, alignment: Optional[int]=1):
        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]

        # Escaped elements don't use the normal struct format, the format is
        # a StarStruct.Message object, but change the mode to match the
        # current mode.
        self.format = field[1]

        self.escapor = Escapor(**field[2]['escape'])

        self._mode = mode
        self._alignment = alignment
        self.update(mode, alignment)

    @staticmethod
    def valid(field: tuple) -> bool:
        """
        See :py:func:`starstruct.element.Element.valid`

        :param field: The items to determine the structure of the element
        """
        if len(field) == 3:
            return isinstance(field[1], starstruct.message.Message) \
                and isinstance(field[2], dict) \
                and 'escape' in field[2].keys()
        else:
            return False

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All elements that are Variable must reference valid Length elements.
        """
        # TODO: Any validation needed here?
        pass

    def update(self, mode=None, alignment=None):
        """change the mode of the struct format"""
        if self._mode is not None:
            self._mode = mode

        if self._alignment is not None:
            self._alignment = alignment

        self.format.update(self._mode, self._alignment)

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        # When packing use the length of the current element to determine
        # how many elements to pack, not the length element of the message
        # (which should not be specified manually).
        iterator = msg[self.name]

        if not isinstance(iterator, list):
            iterator = [iterator]

        ret = self.escapor.start

        for item in iterator:
            ret += self.format.pack(item)

            ret += self.escapor.separator

        ret += self.escapor.end

        # There is no need to make sure that the packed data is properly
        # aligned, because that should already be done by the individual
        # messages that have been packed.
        return ret

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        # When unpacking a variable element, reference the already unpacked
        # length field to determine how many elements need unpacked.
        ret = []

        # Check the starting value
        if buf[:len(self.escapor.start)] == self.escapor.start:
            buf = buf[len(self.escapor.start):]
        else:
            raise ValueError('Buf did not start with expected start sequence: {0}'.format(
                self.escapor.start.decode()))

        unused = buf

        while True:
            (val, unused) = self.format.unpack_partial(unused)
            ret.append(val)

            if unused[:len(self.escapor.separator)] == self.escapor.separator:
                unused = unused[len(self.escapor.separator):]
            else:
                raise ValueError('Buf did not separate with expected separate sequence: {0}'.format(
                    self.escapor.separator.decode()))

            if unused[:len(self.escapor.end)] == self.escapor.end:
                unused = unused[len(self.escapor.end):]
                break

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
