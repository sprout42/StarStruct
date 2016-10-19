#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for the constant class"""

import unittest

from starstruct.message import Message
from starstruct.modes import Mode


class TestElementConstant(unittest.TestCase):
    def test_one_element(self):
        TestStruct = Message('TestStruct', [
            ('regular', 'B'),                           # Two regular messages
            ('fill_in_later', 'H'),
            ('ending_sequence', 'II', (0xAA, 0xBB)),    # An ending sequence to a message
        ])

        test_data = {
            'regular': 13,
            'fill_in_later': 4,
        }

        made = TestStruct.make(**test_data)
        assert made.regular == 13
        assert made.fill_in_later == 4
        assert made.ending_sequence == (0xAA, 0xBB)

    def test_unpack(self):
        TestStruct = Message('TestStruct', [
            ('regular', 'B'),                           # Two regular messages
            ('fill_in_later', 'H'),
            ('ending_sequence', 'II', (0xAB, 0xBA)),    # An ending sequence to a message
        ], Mode.Little)
        test_data = {
            'regular': 8,
            'fill_in_later': 7,
        }

        test_bytes = b'\x08\x07\x00\xab\x00\x00\x00\xba\x00\x00\x00'

        assert test_bytes == TestStruct.pack(**test_data)

        unpacked = TestStruct.unpack(test_bytes)
        assert unpacked.regular == 8
        assert unpacked.fill_in_later == 7
        assert unpacked.ending_sequence == (0xAB, 0xBA)

    def test_unpack_in_the_middle(self):
        SomeMessage = Message('SomeMessage', [
            ('regular', 'B'),
            ('irregular', 'B'),
            ('confused', 'B'),
        ])

        TestStruct = Message('TestStruct', [
            ('regular', 'B'),
            ('middle_constant', 'II', (0xAB, 0xBA)),
            ('a_variable_length', 'H', 'msg'),
            ('msg', SomeMessage, 'a_variable_length')
        ], Mode.Little)

        test_data = {
            'regular': 8,
            'a_variable_length': 2,
            'msg': [
                {'regular': 4, 'irregular': 0, 'confused': 6},
                {'regular': 5, 'irregular': 2, 'confused': 4},
            ],
        }

        made = TestStruct.make(**test_data)
        assert made.regular == 8
        assert made.middle_constant == (0xAB, 0xBA)

        packed = TestStruct.pack(test_data)
        assert packed == b'\x08\xab\x00\x00\x00\xba\x00\x00\x00\x02\x00\x04\x00\x06\x05\x02\x04'

        unpacked = TestStruct.unpack(packed)
        assert unpacked.regular == 8
        assert unpacked.middle_constant == (0xAB, 0xBA)
