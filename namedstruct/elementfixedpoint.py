# import struct

import re

# from decimal import Decimal

from namedstruct.element import Element
from namedstruct.modes import Mode


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

        # TODO: Do I need a ref here?
        self.ref = None

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
