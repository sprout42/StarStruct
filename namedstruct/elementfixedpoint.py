import struct

from decimal import Decimal

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


