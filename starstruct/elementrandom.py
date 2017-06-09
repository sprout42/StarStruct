"""
The random element class for StarStruct

To be used in the following way:

.. code-block:: python

    import random

    def my_random_length():
        return floor(10 * random.random())

    def my_random_value():
        return random.choice(['a', 'b', 'c'])

    random_generator = RandomInterface('b', my_random_length, my_random_value)

    ExampleMessage = Message('random_message', [
        ('random_ints', '?', random_generator)
    ])

"""

import struct

from starstruct.element import register, Element
from starstruct.modes import Mode

class RandomInterface:
    def __init__(self, packing_format, length_generator, value_generator):
        self.packing_format = packing_format
        self.length_generator = length_generator
        self.value_generator = value_generator

        self.last_generated = None
        self.last_packed = None
        self.last_struct = None

    def generate_length(self):
        value = None

        if callable(self.length_generator):
            value = self.length_generator()
        else:
            value = self.length_generator

        return value

    def generate_value(self)
        value = None

        if callable(self.value_generator):
            value = self.value_generator()
        else:
            value = self.value_generator

        return value

    def generate(self):
        length = self.generate_length()
        self.last_generated = [self.generate_value() for _ in range(length)]

        return self.last_generated

    def packed(self):
        generated = self.generate()

        self.last_struct = struct.Struct(self.packing_format * len(generated))
        self.last_packed = self.last_struct.pack(*generated)
        return self.last_packed

    def reset(self):
        self.last_generated = None
        self.last_packed = None
        self.last_struct = None


@register
class ElementRandom(Element):

    def __init__(self, field, mode=Mode.Native, alignment=1):
        self.name = field[0]
        self.ref = None

        self._random_interface: RandomInterface = field[2]
        self._values = None
        self._packed = None
        self._size = None

        self._mode = mode
        self._alignment = alignment

    def reset(self):
        self._values = None
        self._packed = None
        self._size = None
        self._random_interface.reset()

    @property
    def values(self):
        if self._values:
            return self._values

        self._values = self._random_interface.generate()
        return self._values

    @property
    def packed(self):
        if self._packed:
            return self._packed

        _ = self.values
        self._packed = self._random_interface.last_packed

        return self._packed

    @property
    def size(self):
        if self._size:
            return self._size

        _ = self.packed()
        return self._random_interface.last_struct.size

    def pack(self, msg: dict) -> bytes:
        return self.packed

    def unpack(self, msg: dict, buf: bytes) -> bytes:
        return (self._random_interface.last_struct.unpack_from(buf), buf[self.size:])

    def make(self, msg: dict):
        return self.values
