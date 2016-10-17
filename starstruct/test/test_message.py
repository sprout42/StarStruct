#!/usr/bin/env python3

"""Tests for the starstruct class"""

import unittest

import enum
from starstruct.message import Message
from starstruct.modes import Mode


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2
    three = 3


# pylint: disable=line-too-long,invalid-name
class TestStarStruct(unittest.TestCase):
    """StarStruct module tests"""

    teststruct = [
        ('a', 'b'),                            # signed byte: -128, 127
        ('pad1', '3x'),                        # 3 pad bytes
        ('b', 'H'),                            # unsigned short: 0, 65535
        ('pad2', 'x'),                         # 1 pad byte
        ('c', '10s'),                          # 10 byte string
        ('d', 'x'),                            # 1 pad byte
        ('e', '2H'),                           # 4 unsigned bytes: 0, 2^32-1
        ('type', 'B', SimpleEnum),             # unsigned byte, enum validated
        ('length', 'H', 'vardata'),            # unsigned short length field
        ('vardata',                            # variable length data
         Message('VarTest', [('x', 'B'), ('y', 'B')]),
         'length'),
        ('data', {                             # discriminated data
            SimpleEnum.one: Message('Struct1', [('y', 'B'), ('pad', '3x'), ('z', 'i')]),
            SimpleEnum.two: Message('Struct2', [('z', '20s')]),
            SimpleEnum.three: Message('Struct3', []),
        }, 'type'),
    ]

    testvalues = [
        {
            'a': -128,
            'b': 0,
            'c': '0123456789',
            'e': 0,
            'type': SimpleEnum.one,
            'length': 0,
            'vardata': [],
            'data': {
                'y': 50,
                'z': 0x5577AACC,
            },
        },
        {
            'a': 127,
            'b': 65535,
            'c': 'abcdefghij',
            'e': 0xFFFFFFFF,
            'type': SimpleEnum.two,
            'length': 2,
            'vardata': [
                {'x': 1, 'y': 2},
                {'x': 3, 'y': 4},
            ],
            'data': {
                'z': '0123456789abcdefghij',
            },
        },
        {
            'a': -1,
            'b': 32767,
            'c': '\n\tzyx',
            'e': 0x7FFFFFFF,
            'type': SimpleEnum.three,
            'length': 1,
            'vardata': [
                {'x': 255, 'y': 127},
            ],
            'data': {},
        },
        {
            'a': 100,
            'b': 100,
            'c': 'a0b1c2d3e4',
            'e': 10000,
            'type': SimpleEnum.one,
            'length': 10,
            'vardata': [
                {'x': 255, 'y': 127},
                {'x': 254, 'y': 128},
                {'x': 253, 'y': 129},
                {'x': 252, 'y': 130},
                {'x': 251, 'y': 131},
                {'x': 250, 'y': 132},
                {'x': 249, 'y': 133},
                {'x': 248, 'y': 134},
                {'x': 247, 'y': 135},
                {'x': 246, 'y': 136},
            ],
            'data': {
                'y': 100,
                'z': 2000,
            },
        },
    ]

    testbytes = {
        'little': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00\x01\x00\x00\x32\x00\x00\x00\xCC\xAA\x77\x55',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF\x02\x02\x00\x01\x02\x03\x04\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a',
            b'\xFF\x00\x00\x00\xFF\x7F\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\x7F\x03\x01\x00\xFF\x7F',
            b'\x64\x00\x00\x00\x64\x00\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x10\x27\x00\x00\x01\x0A\x00\xFF\x7F\xFE\x80\xFD\x81\xFC\x82\xFB\x83\xFA\x84\xF9\x85\xF8\x86\xF7\x87\xF6\x88\x64\x00\x00\x00\xD0\x07\x00\x00',
        ],
        'big': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00\x01\x00\x00\x32\x00\x00\x00\x55\x77\xAA\xCC',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF\x02\x00\x02\x01\x02\x03\x04\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a',
            b'\xFF\x00\x00\x00\x7F\xFF\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\x7F\xFF\xFF\xFF\x03\x00\x01\xFF\x7F',
            b'\x64\x00\x00\x00\x00\x64\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x00\x00\x27\x10\x01\x00\x0A\xFF\x7F\xFE\x80\xFD\x81\xFC\x82\xFB\x83\xFA\x84\xF9\x85\xF8\x86\xF7\x87\xF6\x88\x64\x00\x00\x00\x00\x00\x07\xD0',
        ],
    }

    def test_init_invalid_name(self):
        """Test invalid Message names."""

        for name in [None, '', 1, dict(), list()]:
            with self.subTest(name):  # pylint: disable=no-member
                with self.assertRaises(TypeError) as cm:
                    Message(name, self.teststruct)
                self.assertEqual(str(cm.exception), 'invalid name: {}'.format(name))

    def test_init_invalid_mode(self):
        """Test invalid Message modes."""

        for mode in ['=', 'stuff', 0, -1, 1]:
            with self.subTest(mode):  # pylint: disable=no-member
                with self.assertRaises(TypeError) as cm:
                    Message('test', self.teststruct, mode)
                self.assertEqual(str(cm.exception), 'invalid mode: {}'.format(mode))

    def test_init_empty_struct(self):
        """Test an empty Message."""

        val = Message('test', [])
        self.assertEqual(val._tuple._fields, ())  # pylint: disable=protected-access

    def test_pack_little_endian(self):
        """Test pack the test formats."""
        test_msg = Message('test', self.teststruct, Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                packed_msg = test_msg.pack(**self.testvalues[idx])
                self.assertEqual(self.testbytes['little'][idx], packed_msg)

    def test_unpack_little_endian(self):
        """Test unpack the test formats."""
        test_msg = Message('test', self.teststruct, Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                (unpacked_partial_msg, unused) = test_msg.unpack_partial(self.testbytes['little'][idx] + b'\xde\xad')
                self.assertEqual(unused, b'\xde\xad')
                unpacked_msg = test_msg.unpack(self.testbytes['little'][idx])
                expected_tuple = test_msg.make(**self.testvalues[idx])  # pylint: disable=protected-access
                self.assertEqual(unpacked_msg, unpacked_partial_msg)
                self.assertEqual(unpacked_msg, expected_tuple)

    def test_pack_big_endian(self):
        """Test pack the test formats."""
        test_msg = Message('test', self.teststruct, Mode.Big)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                packed_msg = test_msg.pack(**self.testvalues[idx])
                self.assertEqual(self.testbytes['big'][idx], packed_msg)

    def test_unpack_big_endian(self):
        """Test unpack the test formats."""
        test_msg = Message('test', self.teststruct, Mode.Big)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                (unpacked_partial_msg, unused) = test_msg.unpack_partial(self.testbytes['big'][idx] + b'\xde\xad')
                self.assertEqual(unused, b'\xde\xad')
                unpacked_msg = test_msg.unpack(self.testbytes['big'][idx])
                expected_tuple = test_msg.make(**self.testvalues[idx])  # pylint: disable=protected-access
                self.assertEqual(unpacked_msg, unpacked_partial_msg)
                self.assertEqual(unpacked_msg, expected_tuple)
