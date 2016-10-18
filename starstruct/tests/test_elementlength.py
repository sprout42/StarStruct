#!/usr/bin/env python3

"""Tests for the elementlength class"""

import unittest

from starstruct.elementlength import ElementLength


# pylint: disable=line-too-long,invalid-name
class TestElementLength(unittest.TestCase):
    """ElementLength module tests"""

    def test_valid(self):
        """Test field formats that are valid ElementLength elements."""

        test_fields = [
            ('a', 'B', 'data'),    # unsigned byte: 0, 255
            ('b', 'H', 'data'),    # unsigned short: 0, 65535
            ('d', 'L', 'data'),    # unsigned long: 0, 2^32-1
            ('d', 'Q', 'data'),    # unsigned long long: 0, 2^64-1
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementLength.valid(field)
                self.assertTrue(out)

    def test_not_valid(self):
        """Test field formats that are not valid ElementLength elements."""

        test_fields = [
            ('a', '4x', 'data'),   # 4 pad bytes
            ('b', 'z', 'data'),    # invalid
            ('c', '1', 'data'),    # invalid
            ('d', '10s', 'data'),  # 10 byte string
            ('e', '9S', 'data'),   # invalid (must be lowercase)
            ('f', '/', 'data'),    # invalid
            ('g', '?', 'data'),    # bool: 0, 1
            ('h', '10s', 'data'),  # 10 byte string
            ('i', 'b', 'data'),    # unsigned byte: 0, 255
            ('j', 'h', 'data'),    # unsigned short: 0, 65535
            ('k', 'l', 'data'),    # unsigned long: 0, 2^32-1
            ('l', 'B'),            # unsigned byte (no ref string)
        ]

        for field in test_fields:
            with self.subTest(field):  # pylint: disable=no-member
                out = ElementLength.valid(field)
                self.assertFalse(out)
