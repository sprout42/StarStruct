#!/usr/bin/env python3

"""Tests for the elementenum class"""

import unittest

import enum
from starstruct.bitfield import BitField
from starstruct.elementbitfield import ElementBitField


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2


# pylint: disable=blacklisted-name
class StrEnum(enum.Enum):
    """string based enum class for testing message pack/unpack"""
    foo = 'foo'
    bar = 'bar'


# pylint: disable=line-too-long,invalid-name,no-self-use
class TestElementBitField(unittest.TestCase):
    """ElementBitField module tests"""

    def test_invalid_enum(self):
        """Test field formats that are valid ElementBitField elements."""
        # pylint: disable=unused-variable

        with self.assertRaises(TypeError) as cm:
            test_bitfield = BitField(StrEnum)  # noqa: F841
        msg = 'Enum {} members must have integer values'.format(repr(StrEnum))
        self.assertEqual(str(cm.exception), msg)

    def test_not_valid(self):
        """Test field formats that are not valid ElementEnum elements."""

        test_bitfield = BitField(SimpleEnum)

        test_fields = [
            ('a', 'b', SimpleEnum),      # enum field
            ('a', 'b', StrEnum),       # enum field
            ('a', '4x', test_bitfield),  # 4 pad bytes
            ('b', 'z', test_bitfield),   # invalid
            ('c', '1', test_bitfield),   # invalid
            ('e', '9s', test_bitfield),  # invalid (no strings allowed)
            ('d', '/', test_bitfield),   # invalid
            ('f', 'H'),               # unsigned short (no class)
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementBitField.valid(field)
                self.assertFalse(out)

    def test_valid_pack(self):
        """Test packing valid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'b', test_bitfield)  # signed byte: -128, 127
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            ({'a': 2}, b'\x02'),
            ({'a': []}, b'\x00'),
            ({'a': [SimpleEnum.one]}, b'\x01'),
            ({'a': [SimpleEnum.two]}, b'\x02'),
            ({'a': [SimpleEnum.one, SimpleEnum.two]}, b'\x03'),
            ({'a': [1, SimpleEnum.two]}, b'\x03'),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                ret = elem.pack(in_val)
                self.assertEqual(ret, out_val)

    def test_out_of_range_values_pack(self):
        """Test packing invalid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'b', test_bitfield)  # signed byte: -128, 127
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            ({'a': 0}, 0),
            ({'a': -1}, -1),
            ({'a': [0, SimpleEnum.one]}, 0),
            ({'a': [SimpleEnum.one, -1]}, -1),
            ({'a': [SimpleEnum.two, 3]}, 3),
        ]

        msg = '{} is not a valid {}'
        for (in_val, bad_val) in test_values:
            with self.subTest((in_val, bad_val)):  # pylint: disable=no-member
                with self.assertRaises(ValueError) as cm:
                    elem.pack(in_val)
                self.assertEqual(str(cm.exception), msg.format(bad_val, 'SimpleEnum'))

    def test_unpack(self):
        """Test unpacking valid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'b', test_bitfield)  # signed byte: -128, 127
        out = ElementBitField.valid(field)
        self.assertTrue(out)
        elem = ElementBitField(field)
        test_values = [
            (b'\x00', frozenset([])),
            (b'\xFC', frozenset([])),
            (b'\x01', frozenset([SimpleEnum.one])),
            (b'\x02', frozenset([SimpleEnum.two])),
            (b'\x03', frozenset([SimpleEnum.one, SimpleEnum.two])),
            (b'\xF3', frozenset([SimpleEnum.one, SimpleEnum.two])),
            (b'\xAA', frozenset([SimpleEnum.two])),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((in_val, out_val)):  # pylint: disable=no-member
                (ret, unused) = elem.unpack({}, in_val)
                self.assertEqual(unused, b'')
                self.assertEqual(ret, out_val)
