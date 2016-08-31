import struct

import re

from decimal import Decimal

from namedstruct.element import Element
from namedstruct.modes import Mode


def get_lower_bits(num, precision):
    """
    Helper function to convert a decimal value to the bits of fixed point
    """


class ElementFixedPoint(Element):
    """
    A NamedStruct element class for fixed point number fields.

    Uses the built in Decimal class

    Example Usage:

    example_bits = 16
    example_precision = 8
    example_struct = namedstruct.Message('example', [
        ('my_fixed', 'F', example_bits, example_precision)
        ])

    my_data = {
        'my_fixed': '120.0'
    }
    packed_struct = example_struct.make(my_data)

    """

    def __init__(self, field, mode=Mode.Native):
        """Initialize a NamedStruct element object."""

        # TODO: Add checks in the class factory?
        self.name = field[0]
        self.bits = field[2]
        self.precision = field[3]

        # TODO: Do I need a ref here?
        self.ref = None

        self._mode = mode

        format_from_list = str(self.bits) + 'b'
        self.format = mode.value + format_from_list
        self._struct = struct.Struct(self.format)

    @staticmethod
    def valid(field):
        """
        Validation function to determine if a field tuple represents a valid
        fixedpoint element type.

        The basics have already been validated by the Element factory class,
        validate the specific struct format now.
        """
        return len(field) == 4 \
            and isinstance(field[1], str) \
            and re.match(r'\d*F', field[1]) \
            and isinstance(field[2], int) \
            and isinstance(field[3], int) \
            and field[2] > field[3]

    def pack(self, msg):
        """Pack the provided values into the specified buffer."""
        print(msg)
        try:
            self.decimal = Decimal(msg[self.name])
        except:
            self.decimal = Decimal(str(msg[self.name]))

        integer = int(self.decimal // 1)
        top_bits = integer.to_bytes(int((self.bits - self.precision) / 8), self._mode.to_byteorder())
        # top_bits = b'{0:%db}' % (self.bits - self.precision)
        # top_bits = top_bits.format(integer)

        bot_bits = b'0' * self.precision

        print('top_bits:', top_bits.bin)
        print('bot_bits:', bot_bits)
        print('all_bits:', top_bits + bot_bits)
        self._struct.pack(top_bits + bot_bits)
