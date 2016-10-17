#!/usr/bin/env python3

"""Tests for the elementpad class"""

import unittest

from starstruct.elementpad import ElementPad


# pylint: disable=line-too-long,invalid-name
class TestElementPad(unittest.TestCase):
    """ElementPad module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementPad elements."""

        test_fields = [
            ('a', '4x'),   # 4 pad bytes
            ('a', 'x'),    # 1 pad bytes
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementPad.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementPad elements."""

        test_fields = [
            ('b', 'z'),     # invalid
            ('c', '1'),     # invalid
            ('d', '9S'),    # invalid (must be lowercase)
            ('e', '/'),     # invalid
            ('a', 'b'),     # signed byte: -128, 127
            ('b', 'H'),     # unsigned short: 0, 65535
            ('c', '10s'),   # 10 byte string
            ('d', 'L'),     # unsigned long: 0, 2^32-1
            ('e', '?'),     # bool: 0, 1
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementPad.valid(field)
                self.assertFalse(out)
