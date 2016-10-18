#!/usr/bin/env python3

"""Tests for the starstruct class"""

import enum
import struct
import unittest

import pytest

from starstruct.message import Message
# from starstruct.modes import Mode


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2
    three = 3


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

    def test_byte_length_no_data(self):
        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),

        ])
        test_data_no_data = {
            'length_in_objects': 0,
            'vardata': [],
            'length_in_bytes': 0,
            'bytesdata': [],
        }

        made = TestStruct.make(test_data_no_data)
        assert made.length_in_objects == 0
        assert made.vardata == []
        assert made.length_in_bytes == 0
        assert made.bytesdata == []

        packed = TestStruct.pack(test_data_no_data)
        assert packed == \
            struct.pack('H', 0) + \
            struct.pack('H', 0)

    def test_byte_length_some_data(self):
        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),

        ])
        test_data_no_data = {
            'length_in_objects': 1,
            'vardata': [
                {'x': 255, 'y': 127},
            ],
            'length_in_bytes': 2,
            'bytesdata': [
                {'x': 254, 'y': 126},
            ],
        }

        made = TestStruct.make(test_data_no_data)
        assert made.length_in_objects == 1
        assert made.vardata == [
            self.VarTest.make(
                {'x': 255, 'y': 127}
            )]
        assert made.length_in_bytes == 2
        assert made.bytesdata == [
            self.VarTest.make(
                {'x': 254, 'y': 126}
            )]

        packed = TestStruct.pack(test_data_no_data)
        assert packed == \
            struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            struct.pack('H', 2) + \
            struct.pack('BB', 254, 126)

    def test_byte_length_more_data(self):
        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),

        ])

        test_data_no_data = {
            'length_in_objects': 1,
            'vardata': [
                {'x': 255, 'y': 127},
            ],
            'length_in_bytes': 10,
            'bytesdata': [
                {'x': 254, 'y': 126},
                {'x': 25, 'y': 16},
                {'x': 24, 'y': 26},
                {'x': 54, 'y': 17},
                {'x': 25, 'y': 12},
            ],
        }

        made = TestStruct.make(test_data_no_data)
        assert made.length_in_objects == 1
        assert made.vardata == [
            self.VarTest.make(
                {'x': 255, 'y': 127}
            )]
        assert made.length_in_bytes == 10
        assert made.bytesdata == [
            self.VarTest.make(
                {'x': 254, 'y': 126}
            ),
            self.VarTest.make(
                {'x': 25, 'y': 16},
            ),
            self.VarTest.make(
                {'x': 24, 'y': 26},
            ),
            self.VarTest.make(
                {'x': 54, 'y': 17},
            ),
            self.VarTest.make(
                {'x': 25, 'y': 12},
            ),
        ]

        packed = TestStruct.pack(test_data_no_data)
        assert packed == \
            struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            struct.pack('H', 10) + \
            struct.pack('BB', 254, 126) + \
            struct.pack('BB', 25, 16) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 54, 17) + \
            struct.pack('BB', 25, 12)

    def test_unpacking_of_correct_size(self):
        packed_element = \
            struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            struct.pack('H', 10) + \
            struct.pack('BB', 254, 126) + \
            struct.pack('BB', 25, 16) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 54, 17) + \
            struct.pack('BB', 25, 12)

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),
        ])

        unpacked = TestStruct.unpack(packed_element)

        assert unpacked
        assert unpacked.length_in_objects == 1
        assert unpacked.length_in_bytes == 10

    def test_unpacking_of_too_little_bytes(self):
        # Only pack four elements, instead of the five
        packed_element = \
            struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            struct.pack('H', 10) + \
            struct.pack('BB', 254, 126) + \
            struct.pack('BB', 25, 16) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 54, 17)

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),
        ])

        with pytest.raises(struct.error):
            unpacked = TestStruct.unpack(packed_element)
            assert unpacked

    def test_unpacking_of_too_many_bytes(self):
        packed_element = \
            struct.pack('H', 1) + \
            struct.pack('BB', 255, 127) + \
            struct.pack('H', 10) + \
            struct.pack('BB', 254, 126) + \
            struct.pack('BB', 25, 16) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 24, 26) + \
            struct.pack('BB', 54, 17)

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
            (b'length_in_bytes', 'H', 'bytesdata'),
            ('bytesdata', self.VarTest, b'length_in_bytes'),
        ])

        with pytest.raises(ValueError):
            unpacked = TestStruct.unpack(packed_element)
            assert unpacked
