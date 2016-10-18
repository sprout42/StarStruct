#!/usr/bin/env python3

"""Tests for the elementstring class"""

import unittest

from starstruct.elementstring import ElementString


# pylint: disable=line-too-long,invalid-name
class TestElementString(unittest.TestCase):
    """ElementString module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementString elements."""

        test_fields = [
            ('a', 'c'),     # single character
            ('b', '2c'),    # 2 char string
            ('c', '10s'),   # 10 char string (variable)
            ('d', '5p'),    # 5 char string (fixed)
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementString.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementString elements."""

        test_fields = [
            ('a', '4x'),    # 4 pad bytes
            ('b', 'z'),     # invalid
            ('c', '1'),     # invalid
            ('d', '9S'),    # invalid (must be lowercase)
            ('e', '/'),     # invalid
            ('a', 'b'),     # signed byte: -128, 127
            ('b', 'H'),     # unsigned short: 0, 65535
            ('d', 'L'),     # unsigned long: 0, 2^32-1
            ('e', '?'),     # bool: 0, 1
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementString.valid(field)
                self.assertFalse(out)
