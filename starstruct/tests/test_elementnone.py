#!/usr/bin/env python3

"""Tests for the starstruct class"""

import struct
import unittest
from hashlib import md5

from starstruct.message import Message


class TestStarStructNone(unittest.TestCase):
    """StarStruct module tests"""
    # TODO: Clean up these tests, change names, and move a bunch of the items to a helper function

    VarTest = Message('VarTest', [
        ('x', 'B'),
        ('y', 'B'),
    ])

    def test_single_element_1(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        def pack_salt(data):
            return b''.join(item.to_bytes(1, 'little') for item in data)

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
                'unpack': (pack_salt, 'function_data'),
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

    def test_single_element_2(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        def do_nothing(data):
            return data

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
                'unpack': (do_nothing, 'function_data'),
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
        # This is non symmetric for this test, so we can't just check based on the made item
        assert unpacked.function_data == (157, 38, 247, 245, 5, 71, 43, 227, 80, 44, 10, 243, 48, 248, 163, 207)

        # TEMP
        new = unpacked._replace(**{'salted': b'random_salter'})
        assert new.salted == b'random_salter'
        # print(new._asdict())

    def test_single_element_3(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        def double(data):
            return [item * 2 for item in data]

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
                'unpack': (double, 'function_data'),
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
        # This is non symmetric for this test, so we can't just check based on the made item
        assert unpacked.function_data == [314, 76, 494, 490, 10, 142, 86, 454, 160, 88, 20, 486, 96, 496, 326, 414]

    def test_single_element_4(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        def double(data):
            return [item * 2 for item in data]

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        # This one has nothing to do with the original packed message
        CRCedMessage = Message('CRCedMessage', [
            ('data', TestStruct),
            ('salted', None),
            ('function_data', '16B', {
                'make': (pseudo_salted_md5, 'salted', b'data'),
                'pack': (pseudo_salted_md5, 'salted', b'data'),
                'unpack': (double, b'data'),
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
        # This is non symmetric for this test, so we can't just check based on the made item
        assert unpacked.function_data == [4, 0, 2, 4, 6, 8]

    def test_nounpack_function(self):
        def pseudo_salted_md5(salt, original):
            temp_md5 = md5(original)

            if salt is None:
                salt = b''

            return md5(salt + temp_md5.digest()).digest()

        TestStruct = Message('TestStruct', [
            ('length_in_objects', 'H', 'vardata'),
            ('vardata', self.VarTest, 'length_in_objects'),
        ])

        # This one has nothing to do with the original packed message
        ExplicitNone = Message('Explicit', [
            ('data', TestStruct),
            ('salted', None),
            ('function_data', '16B', {
                'make': (pseudo_salted_md5, 'salted', b'data'),
                'pack': (pseudo_salted_md5, 'salted', b'data'),
                'unpack': (None, ),
            }, False),
        ])

        ImplicitNone = Message('Implicit', [
            ('data', TestStruct),
            ('salted', None),
            ('function_data', '16B', {
                'make': (pseudo_salted_md5, 'salted', b'data'),
                'pack': (pseudo_salted_md5, 'salted', b'data'),
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

        made = ExplicitNone.make(test_data)
        assert len(made.data.vardata) == 2
        assert made.data.vardata[0].x == 1
        assert made.data.vardata[0].y == 2

        no_data = made.pack()
        regular = ExplicitNone.pack(**test_data)
        assert regular == no_data

        # Show that there's no room to have the random salter be packed
        len_data = len(no_data) - 16
        assert no_data[0:len_data] == struct.pack('HBBBB', 2, 1, 2, 3, 4)
        assert md5(
            b'random_salter' +
            md5(no_data[0:len_data]).digest()
        ).digest() == no_data[len_data:]

        unpacked = ExplicitNone.unpack(no_data)

        assert unpacked.salted is None
        assert unpacked.function_data == (157, 38, 247, 245, 5, 71, 43, 227, 80, 44, 10, 243, 48, 248, 163, 207)

        made = ImplicitNone.make(test_data)
        assert len(made.data.vardata) == 2
        assert made.data.vardata[0].x == 1
        assert made.data.vardata[0].y == 2

        no_data = made.pack()
        regular = ImplicitNone.pack(**test_data)
        assert regular == no_data

        # Show that there's no room to have the random salter be packed
        len_data = len(no_data) - 16
        assert no_data[0:len_data] == struct.pack('HBBBB', 2, 1, 2, 3, 4)
        assert md5(
            b'random_salter' +
            md5(no_data[0:len_data]).digest()
        ).digest() == no_data[len_data:]

        unpacked = ImplicitNone.unpack(no_data)

        assert unpacked.salted is None
        assert unpacked.function_data == (157, 38, 247, 245, 5, 71, 43, 227, 80, 44, 10, 243, 48, 248, 163, 207)
