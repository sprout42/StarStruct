#!/usr/bin/env python3

"""Tests for the elementfixedpoint class"""

import unittest

from decimal import Decimal

from namedstruct.elementfixedpoint import ElementFixedPoint, get_fixed_bits
from namedstruct.modes import Mode


class TestElementFixedPointHelpers(unittest.TestCase):
    """Test the helpers for this class"""
    def test_invalid_higher_bits(self):
        with self.assertRaises(ValueError):
            get_fixed_bits(257, 16, 8)

        with self.assertRaises(ValueError):
            get_fixed_bits(256, 16, 8)

        with self.assertRaises(ValueError):
            get_fixed_bits('hello', 16, 3)

        with self.assertRaises(ValueError):
            get_fixed_bits(Decimal('20'), 8, 4)

    def test_valid_higher_bits(self):
        """Just make sure these all don't fail"""
        get_fixed_bits(255, 16, 8)
        get_fixed_bits(15.5, 16, 4)
        get_fixed_bits(22.75, 16, 11)
        get_fixed_bits(Decimal('13.0'), 32, 16)

    def test_zero(self):
        assert get_fixed_bits(0, 16, 8, '>H') == (0).to_bytes(2, 'big')

    def test_basic_example(self):
        assert get_fixed_bits(15, 8, 4, '<B') == (15 * 2**4).to_bytes(1, 'little')


class TestElementFixedPoint(unittest.TestCase):
    """ElementFixedPoint module tests"""

    def test_valid(self):
        """Test field formats that are valid fixedpoint elements."""

        test_fields = [
            ('a', 'F', 16, 8),
            ('b', '3F', 8, 4),
            ('c', 'F', 8, 7),
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

        field = ('a', 'F', 16, 8)
        self.assertTrue(ElementFixedPoint.valid(field))
        elem = ElementFixedPoint(field, Mode.Big)

        test_values = [
            ({'a': '4'}, b'0000010000000000'),
            ({'a': 13.5}, 0),
            ({'a': '13.5'}, 0),
            ({'a': '13.500'}, 0),
        ]

        for (in_val, out_val) in test_values:
            with self.subTest((out_val, in_val)):  # pylint: disable=no-member
                ret = elem.pack(in_val)
                self.assertEqual(ret, out_val)
