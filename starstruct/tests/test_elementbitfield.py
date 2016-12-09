#!/usr/bin/env python3

"""Tests for the elementenum class"""

import unittest

import struct
import enum
from starstruct.bitfield import BitField
from starstruct.packedbitfield import PackedBitField
from starstruct.elementbitfield import ElementBitField


class SimpleEnum(enum.Enum):
    """Simple enum class for testing message pack/unpack"""
    one = 1
    two = 2
    four = 4


class SimpleEnumWithZero(enum.Enum):
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
class TestElementBitField(unittest.TestCase):
    """ElementBitField module tests"""

    def test_invalid_enum(self):
        """Test field formats that are valid ElementBitField elements."""
        # pylint: disable=unused-variable

        with self.assertRaises(TypeError) as cm:
            test_bitfield = BitField(StrEnum)  # noqa: F841
        msg = 'Enum {} members must have integer values'.format(repr(StrEnum))
        self.assertEqual(str(cm.exception), msg)

        with self.assertRaises(TypeError) as cm:
            test_bitfield = BitField(SimpleEnumWithZero)  # noqa: F841
        msg = 'Cannot construct BitField from {} with a value for 0: {}'.format(repr(SimpleEnumWithZero), SimpleEnumWithZero.zero)
        self.assertEqual(str(cm.exception), msg)

        with self.assertRaises(TypeError) as cm:
            test_packedbitfield = PackedBitField(SimpleEnumWithZero, SimpleEnumWithZero)  # noqa: F841
        msg = 'Duplicate fields not allowed: {}'.format((SimpleEnumWithZero, SimpleEnumWithZero))
        self.assertEqual(str(cm.exception), msg)

        test_bitfield = BitField(SimpleEnum)
        with self.assertRaises(TypeError) as cm:
            test_packedbitfield = PackedBitField(SimpleEnum, test_bitfield)  # noqa: F841
        msg = 'Duplicate fields not allowed: {}'.format((SimpleEnum, test_bitfield))
        self.assertEqual(str(cm.exception), msg)

        with self.assertRaises(TypeError) as cm:
            test_packedbitfield = PackedBitField(StrEnum, test_bitfield)  # noqa: F841
        msg = 'Enum {} members must have integer values'.format(repr(StrEnum))
        self.assertEqual(str(cm.exception), msg)

    def test_not_valid(self):
        """Test field formats that are not valid ElementEnum elements."""

        test_bitfield = BitField(SimpleEnum)
        test_packedbitfield = PackedBitField(SimpleEnumWithZero, test_bitfield)

        test_fields = [
            ('a', 'B', SimpleEnum),      # enum field
            ('a', 'B', StrEnum),       # enum field
            ('a', '4x', test_bitfield),  # 4 pad bytes
            ('b', 'z', test_bitfield),   # invalid
            ('b', 'b', test_bitfield),   # invalid
            ('c', '1', test_bitfield),   # invalid
            ('e', '9s', test_bitfield),  # invalid (no strings allowed)
            ('d', '/', test_bitfield),   # invalid
            ('a', '4x', test_packedbitfield),  # 4 pad bytes
            ('b', 'z', test_packedbitfield),   # invalid
            ('c', '1', test_packedbitfield),   # invalid
            ('e', '9s', test_packedbitfield),  # invalid (no strings allowed)
            ('d', '/', test_packedbitfield),   # invalid
            ('f', 'H'),               # unsigned short (no class)
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementBitField.valid(field)
                self.assertFalse(out)

    def test_valid_pack(self):
        """Test packing valid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'B', test_bitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            ({'a': 2}, b'\x02'),
            ({'a': []}, b'\x00'),
            ({'a': None}, b'\x00'),
            ({'a': [SimpleEnum.one]}, b'\x01'),
            ({'a': ['one']}, b'\x01'),
            ({'a': [SimpleEnum.two]}, b'\x02'),
            ({'a': [SimpleEnum.one, SimpleEnum.two]}, b'\x03'),
            ({'a': [1, SimpleEnum.two]}, b'\x03'),
            ({'a': [1, SimpleEnum.two, 'four']}, b'\x07'),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                ret = elem.pack(in_val)
                self.assertEqual(ret, out_val)

        test_packedbitfield = PackedBitField(SimpleEnumWithZero, test_bitfield)
        field = ('a', 'B', test_packedbitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        self.assertEqual(list(test_packedbitfield._fields.keys()), [SimpleEnumWithZero, test_bitfield])
        self.assertEqual(test_packedbitfield._fields[test_bitfield], {'offset': 0, 'mask': 0x07, 'width': 3})
        self.assertEqual(test_packedbitfield._fields[SimpleEnumWithZero], {'offset': 3, 'mask': 0x18, 'width': 2})

        elem = ElementBitField(field)
        test_values = [
            ({'a': []}, b'\x00'),
            ({'a': None}, b'\x00'),
            ({'a': 0}, b'\x00'),  # 0 is a valid SimpleEnumWithZero
            ({'a': 4}, b'\x04'),
            ({'a': [SimpleEnum.one]}, b'\x01'),
            ({'a': [SimpleEnum.two]}, b'\x02'),
            ({'a': [SimpleEnum.one, SimpleEnum.two]}, b'\x03'),
            ({'a': ['zero', SimpleEnumWithZero.one, SimpleEnum.two]}, b'\x0a'),
            ({'a': [SimpleEnumWithZero.two, 'four']}, b'\x14'),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                ret = elem.pack(in_val)
                self.assertEqual(ret, out_val)

    def test_out_of_range_values_pack(self):
        """Test packing invalid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'B', test_bitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            ({'a': -1}, -1),
            ({'a': 3}, 3),
            ({'a': 0}, 0),
            ({'a': [0, SimpleEnum.one]}, 0),
            ({'a': [SimpleEnum.one, -1]}, -1),
            ({'a': [SimpleEnum.two, 3]}, 3),
            ({'a': ['TWO']}, 'TWO'),
        ]

        msg = '{} is not a valid {}'
        for (in_val, bad_val) in test_values:
            with self.subTest((in_val, bad_val)):  # pylint: disable=no-member
                with self.assertRaises(ValueError) as cm:
                    elem.pack(in_val)
                self.assertEqual(str(cm.exception), msg.format(bad_val, 'SimpleEnum'))

        test_packedbitfield = PackedBitField(SimpleEnumWithZero, test_bitfield)
        field = ('a', 'B', test_packedbitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            ({'a': -1}, 'valid', -1),
            ({'a': 3}, 'valid', 3),
            ({'a': ['one']}, 'unique', 'one'),
            ({'a': [1, SimpleEnum.two]}, 'unique', 1),
            ({'a': [1, SimpleEnum.two, 'four']}, 'unique', 1),
            ({'a': [SimpleEnumWithZero.one, -1]}, 'valid', -1),
            ({'a': ['TWO']}, 'valid', 'TWO'),
        ]
        msg = '{} is not a {} {}'
        for (in_val, err_str, bad_val) in test_values:
            with self.subTest((in_val, err_str, bad_val)):  # pylint: disable=no-member
                with self.assertRaises(ValueError) as cm:
                    elem.pack(in_val)
                self.assertEqual(str(cm.exception), msg.format(bad_val, err_str, [SimpleEnumWithZero, test_bitfield]))

    def test_unpack(self):
        """Test unpacking valid enum values."""

        test_bitfield = BitField(SimpleEnum)

        field = ('a', 'B', test_bitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)
        elem = ElementBitField(field)
        test_values = [
            (b'\x00', frozenset([])),
            (b'\xF8', frozenset([])),
            (b'\x01', frozenset([SimpleEnum.one])),
            (b'\x02', frozenset([SimpleEnum.two])),
            (b'\x03', frozenset([SimpleEnum.one, SimpleEnum.two])),
            (b'\xFF', frozenset([SimpleEnum.one, SimpleEnum.two, SimpleEnum.four])),
            (b'\xAA', frozenset([SimpleEnum.two])),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((in_val, out_val)):  # pylint: disable=no-member
                (ret, unused) = elem.unpack({}, in_val)
                self.assertEqual(unused, b'')
                self.assertEqual(ret, out_val)

        test_packedbitfield = PackedBitField(SimpleEnumWithZero, test_bitfield)
        field = ('a', 'B', test_packedbitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            (b'\x00', frozenset([SimpleEnumWithZero.zero])),
            (b'\x01', frozenset([SimpleEnumWithZero.zero, SimpleEnum.one])),
            (b'\x02', frozenset([SimpleEnumWithZero.zero, SimpleEnum.two])),
            (b'\x13', frozenset([SimpleEnumWithZero.two, SimpleEnum.one, SimpleEnum.two])),
            (b'\xAA', frozenset([SimpleEnumWithZero.one, SimpleEnum.two])),
        ]
        for (in_val, out_val) in test_values:
            with self.subTest((in_val, out_val)):  # pylint: disable=no-member
                (ret, unused) = elem.unpack({}, in_val)
                self.assertEqual(unused, b'')
                self.assertEqual(ret, out_val)

    def test_out_of_range_values_unpack(self):
        """Test packing invalid enum values."""

        test_bitfield = BitField(SimpleEnum)

        test_packedbitfield = PackedBitField(SimpleEnumWithZero, test_bitfield)
        field = ('a', 'B', test_packedbitfield)  # unsigned byte: 0, 256
        out = ElementBitField.valid(field)
        self.assertTrue(out)

        elem = ElementBitField(field)
        test_values = [
            (b'\xF8', 3),
        ]
        msg = '{} is not a valid {}'
        for (in_val, bad_val) in test_values:
            with self.subTest((in_val, bad_val)):  # pylint: disable=no-member
                int_in_val = struct.unpack('B', in_val)[0]
                with self.assertRaises(ValueError) as cm:
                    test_packedbitfield.unpack(int_in_val)
                self.assertEqual(str(cm.exception), msg.format(bad_val, 'SimpleEnumWithZero'))

                with self.assertRaises(ValueError) as cm:
                    elem.unpack({}, in_val)
                unpack_msg = 'Value: {0} was not valid for {1}\n\twith msg: {2},\n\tbuf: {3}'.format(
                    int_in_val, test_packedbitfield, {}, in_val)
                self.assertEqual(str(cm.exception), unpack_msg)
