#!/usr/bin/env python3

"""Tests for the elementenum class"""

import unittest

import enum
from starstruct.elementenum import ElementEnum


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    zero = 0
    one = 1
    two = 2


# pylint: disable=blacklisted-name
class StrEnum(enum.Enum):
    """string based enum class for testing message pack/unpack"""
    foo = 'foo'
    bar = 'bar'


# pylint: disable=line-too-long,invalid-name,no-self-use
class TestElementEnum(unittest.TestCase):
    """ElementEnum module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementEnum elements."""

        test_fields = [
            ('a', 'b', SimpleEnum),  # signed byte: -128, 127
            ('b', 'H', SimpleEnum),  # unsigned short: 0, 65535
            ('d', 'L', SimpleEnum),  # unsigned long: 0, 2^32-1
            ('e', '?', SimpleEnum),  # bool: 0, 1
            ('d', '10s', StrEnum),   # 10 byte string
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementEnum.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementEnum elements."""

        test_fields = [
            ('a', '4x', SimpleEnum),  # 4 pad bytes
            ('b', 'z', SimpleEnum),   # invalid
            ('c', '1', SimpleEnum),   # invalid
            ('e', '9S', SimpleEnum),  # invalid (must be lowercase)
            ('d', '/', SimpleEnum),   # invalid
            ('f', 'H'),               # unsigned short (no class)
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementEnum.valid(field)
                self.assertFalse(out)

    def test_valid_pack(self):
        """Test packing valid enum values."""

        field = ('a', 'b', SimpleEnum)  # signed byte: -128, 127
        out = ElementEnum.valid(field)
        self.assertTrue(out)
        elem = ElementEnum(field)
        test_values = [
            ({'a': 0}, b'\x00'),
            ({'a': 2}, b'\x02'),
            ({'a': SimpleEnum.one}, b'\x01'),
            ({'a': SimpleEnum.two}, b'\x02'),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                ret = elem.pack(in_val)
                self.assertEqual(ret, out_val)

    def test_invalid_pack(self):
        """Test packing invalid enum values."""

        field = ('a', 'b', SimpleEnum)  # signed byte: -128, 127
        out = ElementEnum.valid(field)
        self.assertTrue(out)
        elem = ElementEnum(field)
        test_values = [
            {'a': -1},
            {'a': 3},
        ]
        msg = '{} is not a valid {}'
        for val in test_values:
            with self.subTest(val):  # pylint: disable=no-member
                with self.assertRaises(ValueError) as cm:
                    elem.pack(val)
                self.assertEqual(str(cm.exception), msg.format(val['a'], 'SimpleEnum'))

    def test_valid_unpack(self):
        """Test unpacking valid enum values."""

        field = ('a', 'b', SimpleEnum)  # signed byte: -128, 127
        out = ElementEnum.valid(field)
        self.assertTrue(out)
        elem = ElementEnum(field)
        test_values = [
            (SimpleEnum.zero, b'\x00'),
            (SimpleEnum.one, b'\x01'),
            (SimpleEnum.two, b'\x02'),
        ]
        for (out_val, in_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                (ret, unused) = elem.unpack({}, in_val)
                self.assertEqual(unused, b'')
                self.assertEqual(ret, out_val)

    def test_invalid_unpack(self):
        """Test unpacking invalid enum values."""

        field = ('a', 'b', SimpleEnum)  # signed byte: -128, 127
        out = ElementEnum.valid(field)
        self.assertTrue(out)
        elem = ElementEnum(field)
        test_values = [
            (b'\xFF', -1),
            (b'\x03', 3),
            (b'\x7F', 127),
            (b'\x10', 16),
            (b'\x80', -128),
        ]
        msg = '{} is not a valid {}'
        for (in_val, out_val) in test_values:
            with self.subTest((in_val, out_val)):  # pylint: disable=no-member
                with self.assertRaises(ValueError) as cm:
                    elem.unpack({}, in_val)
                self.assertEqual(str(cm.exception), msg.format(out_val, 'SimpleEnum'))
