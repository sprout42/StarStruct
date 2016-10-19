"""
The constant element class for StarStruct

To be used in the following way:

ExampleMessage = Message('constant_message', [
    ('regular', 'B'),                           # Two regular messages
    ('fill_in_later', 'H'),
    ('ending_sequence', 'II', (0xAA, 0xBB)),    # An ending sequence to a message
                                                # that's always the same
])

:todo: Not sure if alignment is working correctly here, or if it needs to do anything

"""

import struct
from typing import Optional, Tuple

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementConstant(Element):
    def __init__(self, field, mode=Mode.Native, alignment=1):
        self.name = field[0]
        self.format = field[1]
        self.values = field[2]

        self._mode = mode
        self._alignment = alignment

    @property
    def _struct(self):
        return struct.Struct(self._mode.value + self.format)

    @property
    def _packed(self):
        return self._struct.pack(*self.values)

    @staticmethod
    def valid(field: list) -> bool:
        """
        Validate whether this field could supply this element with the corect values
        """
        return len(field) == 3 \
            and isinstance(field[0], str) \
            and isinstance(field[1], str) \
            and struct.calcsize(field[1]) \
            and isinstance(field[2], tuple)

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        Constants will alawys be valid
        """
        return True

    def update(self, mode: Optional[Tuple]=None, alignment: Optional[int]=1) -> None:
        """change the mode of the struct format"""
        if mode:
            self._mode = mode

        if alignment:
            self._alignment = alignment

    def pack(self, msg: dict) -> bytes:
        """
        Pack the provided values into the supplied buffer.

        :param msg: The message specifying the values to pack
        """
        return self._packed

    def unpack(self, msg: dict, buf: bytes) -> Tuple[bytes, bytes]:
        """Unpack data from the supplied buffer using the initialized format."""
        return (self._struct.unpack_from(buf), buf[self._struct.size:])

    def make(self, msg: dict):
        """
        Return the expected "made" value

        :param msg: The values to make
        """
        return self.values
