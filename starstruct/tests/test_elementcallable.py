#!/usr/bin/env python3

"""Tests for the starstruct class"""

# import struct
import unittest
from binascii import crc32

import pytest

from starstruct.message import Message
# from starstruct.modes import Mode


# pylint: disable=line-too-long,invalid-name
class TestStarStruct(unittest.TestCase):
    """StarStruct module tests"""

    VarTest = Message('VarTest', [
        ('x', 'B'),
        ('y', 'B'),
    ])

    Repeated = Message('Repeated', [
        ('x', 'B'),
        ('z', 'H'),
    ])

    def test_single_element_2(self):
        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        CRCedMessage = Message('CRCedMessage', [
            ('data', TestStruct),
            ('function_data', 'I', crc32, [b'data']),
        ])

        test_data = {
            'data': {
                'length_in_objects': 2,
                'vardata': [
                    {'x': 1, 'y': 2},
                    {'x': 3, 'y': 4},
                ],
            },
        }

        made = CRCedMessage.make(test_data)
        # assert len(made) == 5
        assert len(made.data.vardata) == 2
        assert made.data.vardata[0].x == 1
        assert made.data.vardata[0].y == 2
        assert made.function_data == crc32(TestStruct.pack(test_data['data']))

    def test_one_element(self):
        def crc32_wrapper(*args):
            return crc32(b''.join(args))

        CompareMessage = Message('CompareMessage', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        CRCedMessage = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            ('function_data', 'I', crc32_wrapper, [b'length_in_objects', b'vardata']),
        ])

        test_data = {
            'length_in_objects': 2,
            'vardata': [
                {'x': 1, 'y': 2},
                {'x': 3, 'y': 4},
            ],
        }

        made = CRCedMessage.make(test_data)
        # assert len(made) == 5
        assert len(made.vardata) == 2
        assert made.vardata[0].x == 1
        assert made.vardata[0].y == 2

        assert made.function_data == crc32(CompareMessage.pack(test_data))

    def test_adding_element(self):
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

    def test_adding_element_list(self):
        def adder(*args):
            return sum(args)

        AdderMessage = Message('AdderMessage', [
            ('item_a', 'H'),
            ('item_b', 'B'),
            ('item_c', 'B'),
            ('item_d', 'B'),
            ('item_e', 'B'),
            # Note, there is no item 'e' in the list of arguments
            ('function_data', 'I', adder, ['item_a', 'item_b', 'item_c', 'item_d']),
        ])

        # Test getting the correct result
        test_data = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
        }

        made = AdderMessage.make(test_data)
        assert made.item_a == 2
        assert made.item_b == 5

        assert made.function_data == 2 + 5 + 7 + 4

        # Check packing and unpacking
        packed = AdderMessage.pack(test_data)
        assert packed == b'\x02\x00\x05\x07\x04\x06\x12\x00\x00\x00'
        assert packed == made.pack()

        unpacked = AdderMessage.unpack(packed)
        assert made == unpacked

        # Test with correct result
        test_data_2 = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
            'function_data': 2 + 5 + 7 + 4,
        }
        made = AdderMessage.make(test_data_2)
        assert made.item_a == 2
        assert made.item_b == 5

        assert made.function_data == 2 + 5 + 7 + 4

        # Test with incorrect result
        test_data_2 = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
            'function_data': -1,
        }

        with pytest.raises(ValueError):
            made = AdderMessage.make(test_data_2)

    def test_no_error_message(self):
        def adder(*args):
            return sum(args)

        AdderMessage = Message('AdderMessage', [
            ('item_a', 'H'),
            ('item_b', 'B'),
            ('item_c', 'B'),
            ('item_d', 'B'),
            ('item_e', 'B'),
            # Note, there is no item 'e' in the list of arguments
            ('function_data', 'I', adder, ['item_a', 'item_b', 'item_c', 'item_d'], False),
        ])

        # Test with incorrect result
        test_data_2 = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
            'function_data': -1,
        }

        made = AdderMessage.make(test_data_2)
        assert made.function_data == -1

    def test_verifying_unpack(self):
        def adder(*args):
            return sum(args)

        AdderMessage = Message('AdderMessage', [
            ('item_a', 'H'),
            ('item_b', 'B'),
            ('item_c', 'B'),
            ('item_d', 'B'),
            ('item_e', 'B'),
            # Note, there is no item 'e' in the list of arguments
            ('function_data', 'I', adder, ['item_a', 'item_b', 'item_c', 'item_d']),
        ])

        # Test getting the correct result
        test_data = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
        }

        made = AdderMessage.make(test_data)
        assert made.item_a == 2
        assert made.item_b == 5

        assert made.function_data == 2 + 5 + 7 + 4

        # Check packing and unpacking
        packed = AdderMessage.pack(test_data)
        assert packed == b'\x02\x00\x05\x07\x04\x06\x12\x00\x00\x00'
        assert packed == made.pack()

        unpacked = AdderMessage.unpack(packed)
        assert made == unpacked

        # Now we modify the data we are going to unpack, and we should get an error
        modified_packed = b'\x02\x00\x05\x07\x04\x06\x11\x11\x11\x11'

        with pytest.raises(ValueError):
            unpacked = AdderMessage.unpack(modified_packed)

        AdderMessageFalse = Message('AdderMessageFalse', [
            ('item_a', 'H'),
            ('item_b', 'B'),
            ('item_c', 'B'),
            ('item_d', 'B'),
            ('item_e', 'B'),
            # Note, there is no item 'e' in the list of arguments
            ('function_data', 'I', adder, ['item_a', 'item_b', 'item_c', 'item_d'], False),
        ])

        # Test getting the correct result
        test_data = {
            'item_a': 2,
            'item_b': 5,
            'item_c': 7,
            'item_d': 4,
            'item_e': 6,
        }

        made = AdderMessageFalse.make(test_data)
        assert made.item_a == 2
        assert made.item_b == 5

        assert made.function_data == 2 + 5 + 7 + 4

        # Check packing and unpacking
        packed = AdderMessageFalse.pack(test_data)
        assert packed == b'\x02\x00\x05\x07\x04\x06\x12\x00\x00\x00'
        assert packed == made.pack()

        unpacked = AdderMessageFalse.unpack(packed)
        assert made == unpacked

        # Now we modify the data we are going to unpack, and we should get an error
        modified_packed = b'\x02\x00\x05\x07\x04\x06\x11\x11\x11\x11'

        # This time it won't fail because we set False for this message
        unpacked = AdderMessageFalse.unpack(modified_packed)
        assert unpacked.item_a == 2
