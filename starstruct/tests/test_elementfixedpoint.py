#!/usr/bin/env python3

"""Tests for the elementfixedpoint class"""

import unittest

from decimal import Decimal

from starstruct.elementfixedpoint import ElementFixedPoint, get_fixed_bits
from starstruct.message import Message
from starstruct.modes import Mode


# pylint: disable=no-self-use
class TestElementFixedPointHelpers(unittest.TestCase):
    """Test the helpers for this class"""
    def test_invalid_formats(self):
        with self.assertRaises(ValueError):
            get_fixed_bits(5, 'Z', 1)

        with self.assertRaises(ValueError):
            get_fixed_bits(8, 'f', 4)

        # TODO: Make sure that it won't accept more than one number?

    def test_valid_formats(self):
        get_fixed_bits(5, 'h', 1)
        get_fixed_bits(15, 'L', 0)

    def test_invalid_higher_bits(self):
        with self.assertRaises(ValueError):
            get_fixed_bits(257, 'i', 8)

        with self.assertRaises(ValueError):
            get_fixed_bits(256, 'i', 8)

        with self.assertRaises(ValueError):
            get_fixed_bits('hello', 'i', 3)

        with self.assertRaises(ValueError):
            get_fixed_bits(Decimal('20'), 'h', 4)

        with self.assertRaises(ValueError):
            get_fixed_bits(42, 'i', 12)

    def test_valid_higher_bits(self):
        """Just make sure these all don't fail"""
        get_fixed_bits(255, 'I', 8)
        get_fixed_bits(15.5, 'I', 4)
        get_fixed_bits(22.75, 'i', 11)
        get_fixed_bits(Decimal('13.0'), 'q', 16)

    def test_zero(self):
        assert get_fixed_bits(0, 'H', 8) == (0).to_bytes(2, 'big')

    def test_basic_example(self):
        assert get_fixed_bits(Decimal('0.9375'), 'B', 4) == (15).to_bytes(1, 'little')

    def test_another_example(self):
        assert get_fixed_bits(Decimal('12.9375'), 'h', 4) == (192 + 15).to_bytes(2, 'little')
        assert get_fixed_bits(Decimal('12.9375'), 'i', 4) == (192 + 15).to_bytes(4, 'little')
        assert get_fixed_bits(Decimal('12.9375'), 'q', 4) == (192 + 15).to_bytes(8, 'little')


class TestElementFixedPoint(unittest.TestCase):
    """ElementFixedPoint module tests"""

    def test_valid(self):
        """Test field formats that are valid fixedpoint elements."""

        test_fields = [
            ('a', 'F', 'i', 8),
            ('b', 'F', 'h', 4),
            ('c', 'F', 'h', 7),
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementFixedPoint.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid fixedpoint elements."""

        test_fields = [
            ('a', 'PF', 16, 8),  # Must have numbers preceding the F
            ('b', '3D', 8, 8),  # D is not a valid prefix. Must be F for fixedpoint
            ('c', 'D', 8.0, 8),  # Must be int, not float
            ('d', 'D', 8, 16),  # bytes must be larger than precision.
            ('e', 'D', 8),  # Must be of length four
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementFixedPoint.valid(field)
                self.assertFalse(out)

    def test_valid_pack(self):
        """Test packing valid fixed point values."""

        precision = 8
        field = ('a', 'F', 'i', precision)
        self.assertTrue(ElementFixedPoint.valid(field))
        elem = ElementFixedPoint(field, Mode.Big)

        test_values = [
            ({'a': '4'}, 4),
            ({'a': 13.5}, 13.5),
            ({'a': '13.5'}, '13.5'),
            ({'a': '13.500'}, '13.500'),
            ({'a': Decimal('13.500')}, '13.500'),
            ({'a': 1.1 + 2.2}, '3.3'),
        ]

        multiplier = 2 ** precision
        for (in_val, out_val) in test_values:
            ret = elem.pack(in_val)

            if not isinstance(out_val, Decimal):
                out_val = Decimal(out_val)

            self.assertEqual(ret, int((out_val * multiplier)).to_bytes(4, 'big'))

    def test_valid_make(self):
        """Test full packing."""
        my_message = Message('my_msg', [
            ('my_fixed', 'F', 'i', 8),
            ('not_specified_fixed', 'F', 'i', 8),
            ('other_fixed', 'F', 'i', 8, 3),
            ('just_a_num', 'i'),
            ('a_string', '32s'),
            ('this_fixed', 'F', 'i', 5),
        ], Mode.Big)

        data = {
            'my_fixed': 1.1 + 2.2,
            'other_fixed': Decimal('1.1') + Decimal('2.2'),
            'not_specified_fixed': Decimal('1.1') + Decimal('2.2'),
            'just_a_num': 16,
            'a_string': '=====================',
            'this_fixed': '1.9375',
        }

        packed = my_message.pack(data)
        unpacked = my_message.unpack(packed)

        assert unpacked.a_string == data['a_string']
        assert unpacked.just_a_num == data['just_a_num']
        assert unpacked.other_fixed == Decimal('3.3')
        assert unpacked.my_fixed == Decimal('3.296875')
        assert unpacked.not_specified_fixed == Decimal('3.296875')
        assert unpacked.this_fixed == Decimal(data['this_fixed'])
