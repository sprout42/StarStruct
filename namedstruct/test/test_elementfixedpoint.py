#!/usr/bin/env python3

"""Tests for the elementfixedpoint class"""

import unittest

from namedstruct.elementfixedpoint import ElementFixedPoint
from namedstruct.modes import Mode


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
