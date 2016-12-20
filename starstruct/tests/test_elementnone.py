#!/usr/bin/env python3

"""Tests for the starstruct class"""

import struct
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

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        def pack_salt(data):
            return md5(data).digest()

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        CRCedMessage = Message('CRCedMessage', [
            ('data', TestStruct),
            ('salted', None),
            ('function_data', '16B', {
                'make': (pseudo_salted_md5, 'salted', b'data'),
                'pack': (pseudo_salted_md5, 'salted', b'data'),
                'unpack': (pack_salt, b'data'),
            }, False),
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

        # Show that there's no room to have the random salter be packed
        len_data = len(no_data) - 16
        assert no_data[0:len_data] == struct.pack('HBBBB', 2, 1, 2, 3, 4)
        assert md5(
            b'random_salter' +
            md5(no_data[0:len_data]).digest()
        ).digest() == no_data[len_data:]

        unpacked = CRCedMessage.unpack(no_data)

        assert unpacked.salted is None
        assert unpacked.function_data == made.function_data

        # TEMP
        new = unpacked._replace(**{'salted': b'random_salter'})
        assert new.salted == b'random_salter'
        # print(new._asdict())
