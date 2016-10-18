#!/usr/bin/env python3

"""Tests for the elementbase class"""

import unittest

from starstruct.elementbase import ElementBase


# pylint: disable=line-too-long,invalid-name,no-self-use
class TestElementBase(unittest.TestCase):
    """ElementBase module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementBase elements."""

        test_fields = [
            ('a', 'd'),     # double
            ('b', 'f'),     # float
            ('e', '?'),     # bool: 0, 1
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementBase.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementBase elements."""

        test_fields = [
            ('a', '4x'),    # 4 pad bytes
            ('b', 'z'),     # invalid
            ('c', '1'),     # invalid
            ('d', '9S'),    # invalid (must be lowercase)
            ('e', 'b'),     # signed byte: -128, 127
            ('f', 'H'),     # unsigned short: 0, 65535
            ('g', '10s'),   # 10 byte string
            ('h', 'L'),     # unsigned long: 0, 2^32-1
            ('i', '/'),     # invalid
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementBase.valid(field)
                self.assertFalse(out)
