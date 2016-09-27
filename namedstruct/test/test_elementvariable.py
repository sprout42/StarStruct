#!/usr/bin/env python3

"""Tests for the namedstruct class"""

import struct
import unittest

import enum
from namedstruct.message import Message
# from namedstruct.modes import Mode


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2
    three = 3


# pylint: disable=line-too-long,invalid-name
class TestNamedstruct(unittest.TestCase):
    """NamedStruct module tests"""

    VarTest = Message('VarTest', [
        ('x', 'B'),
        ('y', 'B'),
    ])

    Repeated = Message('Repeated', [
        ('x', 'B'),
        ('z', 'H'),
    ])

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

    def test_some_data(self):
        num_repeats = 3

        TestStruct = Message('TestStruct', [
            ('length', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length'),
            ('repeated_data', self.Repeated, num_repeats),
        ])

        test_data = {
            'length': 2,
            'vardata': [
                {'x': 1, 'y': 2},
                {'x': 3, 'y': 4},
            ],
            'repeated_data': [
                {'x': 7, 'z': 13},
                {'x': 2, 'z': 27},
                {'x': 6, 'z': 11},
            ],
        }

        made = TestStruct.make(test_data)
        assert made.length == 2
        assert len(made.vardata) == 2
        assert len(made.repeated_data) == 3

        packed = TestStruct.pack(test_data)
        assert packed == struct.pack('H', 2) + \
            struct.pack('BB', 1, 2) + \
            struct.pack('BB', 3, 4) + \
            (struct.pack('B', 7) + struct.pack('H', 13)) + \
            (struct.pack('B', 2) + struct.pack('H', 27)) + \
            (struct.pack('B', 6) + struct.pack('H', 11))

    def test_not_all_fixed_data(self):
        num_repeats = 5

        TestStruct = Message('TestStruct', [
            ('length', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length'),
            ('repeated_data', self.Repeated, num_repeats),
        ])

        test_data = {
            'length': 1,
            'vardata': [
                {'x': 255, 'y': 127},
            ],
            'repeated_data': [
                {'x': 6, 'z': 12},
                {'x': 1, 'z': 26},
                {'x': 5, 'z': 10},
            ],
        }

        made = TestStruct.make(test_data)
        assert made.length == 1
        assert len(made.vardata) == 1
        assert len(made.repeated_data) == 3

        packed = TestStruct.pack(test_data)
        assert packed == struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            (struct.pack('B', 6) + struct.pack('H', 12)) + \
            (struct.pack('B', 1) + struct.pack('H', 26)) + \
            (struct.pack('B', 5) + struct.pack('H', 10)) + \
            (struct.pack('B', 0) + struct.pack('H', 0)) * 2
