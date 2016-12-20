"""
Element callable.

Call a function to validate data.

TODO: Update the format here

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
    accepted_mesages = (True, False)

    # pylint: disable=too-many-instance-attributes
    def __init__(self, field: list, mode: Optional[Mode]=Mode.Native, alignment: Optional[int]=1):
        # All of the type checks have already been performed by the class
        # factory
        self.name = field[0]

        # Callable elements use the normal struct packing method
        self.format = field[1]

        if isinstance(field[2], dict):
            self.ref = field[2]

            default_list = [None, None]
            self._make_func = self.ref.get('make', default_list)[0]
            self._make_args = self.ref.get('make', default_list)[1:]

            self._pack_func = self.ref.get('pack', default_list)[0]
            self._pack_args = self.ref.get('pack', default_list)[1:]

            self._unpack_func = self.ref.get('unpack', default_list)[0]
            self._unpack_args = self.ref.get('unpack', default_list)[1:]
        elif isinstance(field[2], set):
            instruction = field[2].copy().pop()
            self.ref = {'all': instruction}

            self._make_func = self._pack_func = self._unpack_func = instruction[0]
            self._make_args = self._pack_args = self._unpack_args = instruction[1:]

        if len(field) == 4:
            self._error_on_bad_result = field[3]
        else:
            self._error_on_bad_result = True

        self._elements = []

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
        required_keys = {'pack', 'unpack', 'make'}

        if len(field) >= 3 and isinstance(field[0], str) and isinstance(field[1], str):
            if isinstance(field[2], dict):
                if set(field[2].keys()) <= required_keys and \
                        all(isinstance(val, tuple) for val in field[2].values()):
                    return True
            elif isinstance(field[2], set):
                return len(field[2]) == 1 and \
                    all(isinstance(val, tuple) for val in field[2])

        return False


    def validate(self, msg):
        """
        Ensure that the supplied message contains the required information for
        this element object to operate.

        All elements that are Variable must reference valid Length elements.
        """
        for action in self.ref.values():
            for arg in action[1:]:
                if arg in ElementCallable.accepted_mesages:
                    continue
                elif isinstance(arg, str):
                    pass
                elif hasattr(arg, 'decode'):
                    arg = arg.decode('utf-8')
                elif hasattr(arg, 'to_bytes'):
                    arg = arg.to_bytes((arg.bit_length() + 7) // 8, self._mode.to_byteorder()).decode('utf-8')

                if arg not in msg:
                    raise ValueError('Need all keys to be in the message, {0} was not found\nAction: {1} -> {2}'.format(arg, action, action[1:]))

    def update(self, mode=None, alignment=None):
        """change the mode of the struct format"""
        if mode:
            self._mode = mode

        if alignment:
            self._alignment = alignment

    def pack(self, msg):
        """Pack the provided values into the supplied buffer."""
        pack_values = self.call_func(msg, self._pack_func, self._pack_args)

        # Test if the object is iterable
        # If it isn't, then turn it into a list
        try:
            _ = (p for p in pack_values)
        except TypeError:
            pack_values = [pack_values]

        # Unpack the items for struct to allow for mutli-value
        # items to be passed in.
        return self._struct.pack(*pack_values)

    def unpack(self, msg, buf):
        """Unpack data from the supplied buffer using the initialized format."""
        ret = self._struct.unpack_from(buf)
        if isinstance(ret, (list, tuple)) and len(ret) == 1:
            # We only change it not to a list if we expected one value.
            # Otherwise, we keep it as a list, because that's what we would
            # expect (like for a 16I type of struct
            ret = ret[0]

        # Only check for errors if they haven't told us not to
        if self._error_on_bad_result:
            # Pretend we're getting a dictionary to make our item,
            # but it has no reference to `self`. This is so we check
            # for errors correctly.
            temp_dict = copy.deepcopy(msg._asdict())
            temp_dict.pop(self.name)
            expected_value = self.call_func(msg, self._unpack_func, self._unpack_args)

            # Check for an error
            if expected_value != ret:
                raise ValueError('Expected value was: {0}, but got: {1}'.format(
                    expected_value,
                    ret,
                ))

        if self.name in self._unpack_args:
            msg = msg._replace(**{self.name: ret})

        ret = self.call_func(msg, self._unpack_func, self._unpack_args, original=ret)

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

        ret = self.call_func(msg, self._make_func, self._make_args)

        if self.name in msg:
            if ret != msg[self.name]:
                raise ValueError('Excepted value: {0}, but got: {1}'.format(ret, msg[self.name]))

        return ret

    def call_func(self, msg, func, args, original=None):
        if func is None:
            return original

        items = self.prepare_args(msg, args)
        return func(*items)

    def prepare_args(self, msg, args):
        items = []

        if hasattr(msg, '_asdict'):
            msg = msg._asdict()

        for reference in args:
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

        return items
