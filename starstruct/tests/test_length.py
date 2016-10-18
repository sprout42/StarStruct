#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import struct
import unittest

import pytest

from starstruct.message import Message


class MyEnum(enum.Enum):
    """Possible enum types."""
    THIS = 0
    THAT = 1
    OTHER = 2


MyNamed = Message('MyNamed', [
    ('type', 'B'),
    ('name', '32s'),
])

MyOtherNamed = Message('MyOtherNamed', [
    ('first', 'B'),
    ('second', 'H'),
    ('pad', '30x'),
])

NotSameMessage = Message('WowNotEvenClose', [
    ('first_and_only', '4H')
])


# pylint: disable=no-self-use
class TestLengthHelper(unittest.TestCase):
    """Test the length for this class"""
    def test_empty_length(self):
        empty_message = Message('Empty', [])
        assert len(empty_message) == 0

    def test_single_item(self):
        one_message = Message('One', [
            ('info', 'H'),
        ])
        assert len(one_message) == struct.calcsize('H')

    def test_comparison(self):
        assert len(MyNamed) == len(MyOtherNamed)
        assert len(MyNamed) != len(NotSameMessage)

    def test_bad_length_item(self):
        bad_message = Message('BadMessage', [
            ('type', 'B', MyEnum),
            ('data', {
                MyEnum.THIS: MyNamed,
                MyEnum.THAT: NotSameMessage,
                MyEnum.OTHER: MyOtherNamed,
            }, 'type'),
        ])

        with self.assertRaises(AttributeError):
            print(len(bad_message))

    def test_long_item(self):
        long_message = Message('ThisIsALongOne', [
            ('ID', 'B'),
            ('delay', 'B'),
            ('a_byte', 'B'),
            ('type', 'B', MyEnum),
            ('data', {
                MyEnum.THIS: MyNamed,
                MyEnum.THAT: MyNamed,
                MyEnum.OTHER: MyOtherNamed,
            }, 'type'),
        ])

        # Second size is from the MyNamed Enum above
        my_named_format = 'B32s'
        assert len(long_message) == struct.calcsize('BBBB' + my_named_format)

    @pytest.mark.skip(reason="don't know how to test this")
    def test_variable_length(self):
        dont_know_how_to_test = Message('DontKnow', [
            ('numNames', 'B', 'names'),
            ('names', MyNamed, 'numNames'),
        ])

        # Not sure how to test this one yet
        # could do some multiples thing or just let it be.
        print(len(dont_know_how_to_test))
