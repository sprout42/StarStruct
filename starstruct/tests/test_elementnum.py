#!/usr/bin/env python3

"""Tests for the elementbase class"""

import unittest

from starstruct.elementnum import ElementNum


# pylint: disable=line-too-long,invalid-name
class TestElementNum(unittest.TestCase):
    """ElementNum module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementNum elements."""

        test_fields = [
            ('a', '3b'),    # 3 byte number: 0, 2^24-1
            ('b', 'H'),     # unsigned short: 0, 65535
            ('c', '4Q'),    # 32 signed byte number: (super big number)
            ('d', 'l'),     # signed long: -2^31, 2^31-1
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementNum.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementNum elements."""

        test_fields = [
            ('a', '4x'),    # 4 pad bytes
            ('b', 'z'),     # invalid
            ('c', '1'),     # invalid
            ('d', '9S'),    # invalid (must be lowercase)
            ('e', '/'),     # invalid
            ('f', '?'),     # invalid
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementNum.valid(field)
                self.assertFalse(out)
