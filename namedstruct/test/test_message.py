#!/usr/bin/env python3

"""Tests for the namedstruct class"""

import unittest

import enum
import namedstruct as ns


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2
    three = 3


# pylint: disable=line-too-long,invalid-name
class TestNamedstruct(unittest.TestCase):
    """NamedStruct module tests"""

    # structure used for all tests, exercises a range of struct formats.  It
    # isn't necessary to test them all because we don't need to test all of the
    # struct module, just enough to ensure that the values and patterns are
    # matched up properly by the NamedStruct class.
    #
    # Total size of this format is 18 bytes.
    teststruct = [
        ('a', 'b'),              # signed byte: -128, 127
        ('pad1', '3x'),          # 3 pad bytes
        ('b', 'H'),              # unsigned short: 0, 65535
        ('pad2', 'x'),           # 1 pad byte
        ('c', '10s'),            # 10 byte string
        ('d', 'x'),              # 1 pad byte
        ('e', 'L'),              # unsigned long: 0, 2^32-1
        ('f', 'B', SimpleEnum),  # unsigned byte, enum validated
    ]

    testvalues = [
        {'a': -128, 'b': 0, 'c': b'0123456789', 'e': 0, 'f': SimpleEnum.one},
        {'a': 127, 'b': 65535, 'c': b'abcdefghij', 'e': 0xFFFFFFFF, 'f': SimpleEnum.two},
        {'a': -1, 'b': 32767, 'c': b'\n\tzyx\0\0\0\0\0', 'e': 0x7FFFFFFF, 'f': SimpleEnum.three},
        {'a': 100, 'b': 100, 'c': b'a0b1c2d3e4', 'e': 10000, 'f': SimpleEnum.one},
    ]

    testbytes = {
        'little': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00\x01',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF\x02',
            b'\xFF\x00\x00\x00\xFF\x7F\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\x7F\x03',
            b'\x64\x00\x00\x00\x64\x00\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x10\x27\x00\x00\x01',
        ],
        'big': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00\x01',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF\x02',
            b'\xFF\x00\x00\x00\x7F\xFF\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\x7F\xFF\xFF\xFF\x03',
            b'\x64\x00\x00\x00\x00\x64\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x00\x00\x27\x10\x01',
        ],
    }

    def test_init_invalid_name(self):
        """Test invalid Message names."""

        for name in [None, '', 1, dict(), list()]:
            with self.subTest(name):  # pylint: disable=no-member
                with self.assertRaises(TypeError) as cm:
                    ns.Message(name, self.teststruct)
                self.assertEqual(str(cm.exception), 'invalid name: {}'.format(name))

    def test_init_invalid_mode(self):
        """Test invalid Message modes."""

        for mode in ['=', 'stuff', 0, -1, 1]:
            with self.subTest(mode):  # pylint: disable=no-member
                with self.assertRaises(TypeError) as cm:
                    ns.Message('test', self.teststruct, mode)
                self.assertEqual(str(cm.exception), 'invalid mode: {}'.format(mode))

    def test_init_empty_struct(self):
        """Test an empty Message."""

        val = ns.Message('test', [])
        self.assertEqual(val._tuple._fields, ())  # pylint: disable=protected-access

    def test_pack_little_endian(self):
        """Test pack the test formats."""
        test_msg = ns.Message('test', self.teststruct, ns.modes.Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                packed_msg = test_msg.pack(**self.testvalues[idx])
                self.assertEqual(self.testbytes['little'][idx], packed_msg)

    def test_unpack_little_endian(self):
        """Test unpack the test formats."""
        test_msg = ns.Message('test', self.teststruct, ns.modes.Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                (unpacked_msg, unused) = test_msg.unpack(self.testbytes['little'][idx])
                self.assertEqual(unused, b'')
                expected_tuple = test_msg._tuple(**self.testvalues[idx])  # pylint: disable=protected-access
                self.assertEqual(unpacked_msg, expected_tuple)

    def test_pack_big_endian(self):
        """Test pack the test formats."""
        test_msg = ns.Message('test', self.teststruct, ns.modes.Mode.Big)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):  # pylint: disable=no-member
                packed_msg = test_msg.pack(**self.testvalues[idx])
                self.assertEqual(self.testbytes['big'][idx], packed_msg)
