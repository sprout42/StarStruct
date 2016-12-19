#!/usr/bin/env python3

"""Tests for the starstruct class"""

import unittest
from hashlib import md5

from starstruct.message import Message


class TestStarStructNone(unittest.TestCase):
    """StarStruct module tests"""

    VarTest = Message('VarTest', [
        ('x', 'B'),
        ('y', 'B'),
    ])

    def test_single_element_2(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)
            return md5(salt + temp_md5.digest()).digest()

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        CRCedMessage = Message('CRCedMessage', [
            ('data', TestStruct),
            ('salted', None),
            ('function_data', '16B', pseudo_salted_md5, ['salted', b'data']),
        ])

        test_data = {
            'data': {
                'length_in_objects': 2,
                'vardata': [
                    {'x': 1, 'y': 2},
                    {'x': 3, 'y': 4},
                ],
            },
            'salted': b'random_salter',
        }

        made = CRCedMessage.make(test_data)
        # assert len(made) == 5
        assert len(made.data.vardata) == 2
        assert made.data.vardata[0].x == 1
        assert made.data.vardata[0].y == 2

        no_data = made.pack()
        regular = CRCedMessage.pack(**test_data)
        assert regular == no_data
