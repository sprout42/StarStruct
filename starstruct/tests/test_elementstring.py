#!/usr/bin/env python3

"""Tests for the elementstring class"""

import unittest

import pytest

from starstruct.message import Message
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

    def test_make_andk_pack(self):
        """Test field formats that are valid ElementString elements."""
        TestStruct = Message('TestStruct', [
            ('a', 'c'),     # single character
            ('b', '2c'),    # 2 char string
            ('c', '10s'),   # 10 char string (variable)
            ('d', '9p'),    # 9 ( - 1 ) char string (fixed)
            ('e', '5c'),
        ])

        test_data = {
            'a': 'i',
            'b': 'hi',
            'c': 'short',
            'd': 'long',
            'e': ['l', 'i', 's', 't'],
        }

        made = TestStruct.make(test_data)

        assert made.a == ['i']
        assert made.b == ['h', 'i']
        assert made.c == 'short'
        assert made.d == 'long\x00\x00\x00\x00'
        assert made.e == ['l', 'i', 's', 't', '\x00']

        packed = TestStruct.pack(test_data)
        unpacked = TestStruct.unpack(packed)

        assert made == unpacked

    def test_alignment(self):
        """Test field formats that are valid ElementString elements."""
        TestStruct = Message('TestStruct', [
            ('a', 'c'),     # single character
            ('b', '2c'),    # 2 char string
        ])

        test_data = {
            'a': 'a',
            'b': 'no',
        }

        TestStruct.update(alignment=4)
        packed = TestStruct.pack(test_data)
        assert packed == b'a\x00\x00\x00no\x00\x00'

    def test_bad_values(self):
        """Test field formats that are valid ElementString elements."""
        TestStruct = Message('TestStruct', [
            ('a', 'c'),     # single character
            ('b', '2c'),    # 2 char string
        ])

        test_data = {
            'a': [5],
            'b': 'no',
        }

        with pytest.raises(TypeError):
            TestStruct.make(test_data)
