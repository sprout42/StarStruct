"""
Element callable.

Call a function to validate data.

.. code-block:: python

    from binascii import crc32

    ExampleMessage = Message('VarTest', [('x', 'B'), ('y', 'B')])

    CRCedMessage = Message('CRCedMessage', [
       ('data', ExampleMessage),                    # A data field that has the example message in it
       ('crc', 'I', crc32, ['data']),               # Crc the data, and give an error if we have something unexpected
       ('crc', 'I', crc32, ['data'], False),        # Crc the data, but don't give an error
   ])

Following creating this message, you have two options:

1. Specify a value. The function will be used to validate the value.

.. code-block:: python

    def adder(x, y):
        return x + y

    AdderMessage = Message('AdderMessage', [
        ('item_a', 'H'),
        ('item_b', 'B'),
        ('function_data', 'I', adder, ['item_a', 'item_b']),
    ])

    test_data = {
        'item_a': 2,
        'item_b': 5,
        'function_data': 7,
    }

    made = AdderMessage.make(test_data)
    assert made.item_a == 2
    assert made.item_b == 5
    assert made.function_data == 7

    # If you specify the wrong value, you'll get a ValueError
    test_data = {
        'item_a': 2,
        'item_b': 5,
        'function_data': 33,
    }

    try:
        made = AdderMessage.make(test_data)
    except ValueError:
        print('Told you so')

    # Unless you specify `False` in your original item, then
    # nobody will care.

2. Use the function to generate a value.

.. code-block:: python

    def adder(x, y):
        return x + y

    AdderMessage = Message('AdderMessage', [
        ('item_a', 'H'),
        ('item_b', 'B'),
        ('function_data', 'I', adder, ['item_a', 'item_b']),
    ])

    test_data = {
        'item_a': 2,
        'item_b': 5,
    }

    made = AdderMessage.make(test_data)
    assert made.item_a == 2
    assert made.item_b == 5
    assert made.function_data == 7

"""

import copy
import struct

from typing import Optional

from starstruct.element import register, Element
from starstruct.modes import Mode


@register
class ElementCallable(Element):
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

        # Callable elements use the normal struct packing method
        self.format = field[1]
        self._func_ref = field[2]
        self._func_args = field[3]

        if len(field) == 5:
            self._error_on_bad_result = field[4]
        else:
            self._error_on_bad_result = True

        self.update(mode, alignment)

    @property
    def _struct(self):
        return struct.Struct(self._mode.value + self.format)

    @staticmethod
    def valid(field: tuple) -> bool:
        """
        See :py:func:`starstruct.element.Element.valid`

        :param field: The items to determine the structure of the element
        """
        return len(field) >= 4 \
            and isinstance(field[0], str) \
            and isinstance(field[1], str) \
            and callable(field[2]) \
            and isinstance(field[3], list)

    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All elements that are Variable must reference valid Length elements.
        """
        # TODO: Validate the object
        self._elements = msg

        if not all(k in msg
                   for k in [arg if isinstance(arg, str) else arg.decode('utf-8')
                             for arg in self._func_args]):
            raise ValueError('Need all keys to be in the message')

        pass

    def update(self, mode=None, alignment=None):
        """change the mode of the struct format"""
        if mode:
            self._mode = mode

        if alignment:
            self._alignment = alignment

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        return self._struct.pack(self.make(msg))

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        ret = self._struct.unpack_from(buf)
        if isinstance(ret, (list, tuple)):
            # TODO: I don't know if there is a case where we want to keep
            # it as a list... but for now I'm just going to do this
            ret = ret[0]

        # Only check for errors if they haven't told us not to
        if self._error_on_bad_result:
            # Pretend we're getting a dictionary to make our item,
            # but it has no reference to `self`. This is so we check
            # for errors correctly.
            temp_dict = copy.deepcopy(msg._asdict())
            temp_dict.pop(self.name)
            expected_value = self.make(temp_dict)

            # Check for an error
            if expected_value != ret:
                raise ValueError('Expected value was: {0}, but got: {1}'.format(
                    expected_value,
                    ret,
                ))

        return (ret, buf[self._struct.size:])

    def make(self, msg):
        """Return the expected "made" value"""
        # If we aren't going to error on a bad result
        # and our name is in the message, just send the value
        # No need to do extra work.
        if not self._error_on_bad_result \
                and self.name in msg \
                and msg[self.name] is not None:
            return msg[self.name]

        items = []

        for reference in self._func_args:
            if isinstance(reference, str):
                index = reference
                attr = 'make'
            elif isinstance(reference, bytes):
                index = reference.decode('utf-8')
                attr = 'pack'
            else:
                raise ValueError('Needed str or bytes for the reference')

            items.append(
                getattr(self._elements[index], attr)(msg)
            )

        ret = self._func_ref(*items)

        if self.name in msg:
            if ret != msg[self.name]:
                raise ValueError('Excepted value: {0}, but got: {1}'.format(ret, msg[self.name]))

        return ret
