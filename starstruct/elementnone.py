"""
Element None

A non-packable, non-unpackable item that can help facilitate with additional information about an object,
pass extra references to a variable and potentially more

.. code-block:: python

    ExampleMessage = Message('VarTest', [('x', 'B'), ('y', 'B')])

    CRCedMessage = Message('CRCedMessage', [
       ('data', ExampleMessage),                  # A data field that has the example message in it
       ('extra_param', None),                     # The None Element
       ('crc', 'I', my_crc32, ['data', 'extra_param']),          # Crc the data, and give an error if we have something unexpected
   ])

"""

from typing import Optional

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementNone(Element):
    """
    Initialize a StarStruct element object.

    :param field: The fields passed into the constructor of the element
    :param mode: The mode in which to pack the bytes
    :param alignment: Number of bytes to align to
    """
    def __init__(self, field: list, mode: Optional[Mode]=Mode.Native, alignment: Optional[int]=1):
        self.name = field[0]

        self.update(mode=mode, alignment=alignment)

    @staticmethod
    def valid(field: tuple) -> bool:
        return len(field) == 2 \
            and isinstance(field[0], str) \
            and field[1] is None

    def validate(self, msg):
        return True

    def update(self, mode=None, alignment=None):
        if mode:
            self._mode = mode

        if alignment:
            self._alignment = alignment
        return

    def pack(self, msg):
        return b''

    def unpack(self, msg, buf):
        return (msg, buf)

    def make(self, msg):
        return msg[self.name]
