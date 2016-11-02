#!/usr/bin/env python3

"""Tests for the starstruct class and its self packing"""

import struct
import unittest

from starstruct.message import Message


class TestStarStruct(unittest.TestCase):
    """Test class for self packing of messages"""

    teststruct = [
        ('a', 'b'),                            # signed byte: -128, 127
        ('pad1', '3x'),                        # 3 pad bytes
        ('b', 'H'),                            # unsigned short: 0, 65535
        ('pad2', 'x'),                         # 1 pad byte
    ]

    testvalues = [
        {
            'a': -128,
            'b': 0,
        },
        {
            'a': 127,
            'b': 65535,
        },
    ]

    VarTest = Message('VarTest', [
        ('x', 'B'),
        ('y', 'B'),
    ])

    Repeated = Message('Repeated', [
        ('x', 'B'),
        ('z', 'H'),
    ])

    def test_self_pack(self):
        my_message = Message('MyMessage', self.teststruct)

        my_instance_1 = my_message.make(self.testvalues[0])
        my_instance_2 = my_message.make(self.testvalues[1])

        my_bytes_1 = my_message.pack(self.testvalues[0])
        my_bytes_2 = my_message.pack(self.testvalues[1])

        assert my_instance_1.pack() == my_bytes_1
        assert my_instance_2.pack() == my_bytes_2

    def test_no_data(self):
        num_repeats = 4

        TestStruct = Message('TestStruct', [
            ('length', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length'),
            ('repeated_data', self.Repeated, num_repeats),
        ])
        test_data_no_data = {
            'length': 0,
            'vardata': [],
            'repeated_data': [
            ],
        }

        made = TestStruct.make(test_data_no_data)
        assert made.length == 0
        assert made.vardata == []
        assert made.repeated_data == []

        packed = TestStruct.pack(test_data_no_data)
        assert packed == struct.pack('H', 0) + (struct.pack('B', 0) + struct.pack('H', 0)) * num_repeats
        assert packed == made.pack()
