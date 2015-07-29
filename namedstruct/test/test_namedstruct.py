#!/usr/bin/env python3

"""Tests for the namedstruct class"""

import collections
import unittest

from namedstruct import struct as ns
from namedstruct import modes
import struct


class TestNamedstruct(unittest.TestCase):

    """NamedStruct tests"""

    # structure used for all tests, exercises a range of struct formats.  It
    # isn't necessary to test them all because we don't need to test all of the
    # struct module, just enough to ensure that the values and patterns are
    # matched up properly by the NamedStruct class.
    #
    # Total size of this format is 18 bytes.
    teststruct = [
        ('a', 'b'),     # signed byte: -128, 127
        ('pad', '3x'),  # 3 pad bytes
        ('b', 'H'),     # unsigned short: 0, 65535
        ('pad', 'x'),   # 1 pad byte
        ('c', '10s'),   # 10 byte string
        ('d', 'x'),     # 1 pad byte
    ]

    def test_init_invalid_name(self):
        """Test invalid NamedStruct names."""

        for name in [None, '', 1, dict(), list()]:
            with self.subTest(name):
                msg = 'invalid name: {}'.format(name)
                with self.assertRaises(TypeError, msg=msg):
                    ns.NamedStruct(name, self.teststruct)

    def test_init_invalid_mode(self):
        """Test invalid NamedStruct modes."""

        for mode in ['=', 'stuff', 0, -1, 1]:
            with self.subTest(mode):
                msg = 'invalid mode: {}'.format(mode)
                with self.assertRaises(TypeError, msg=msg):
                    ns.NamedStruct('test', self.teststruct, mode)

    def test_init_invalid_fields(self):
        """Test invalid NamedStruct fields."""

        """
        Invalid fields are format specifiers that are not accepted by the
        Struct class.  Valid fields are identified in here:
        https://docs.python.org/3/library/ns.html#format-characters

        Append the invalid field to the end of the standard test structure and
        ensure it fails.  Test invalid characters and an invalid trailing
        number.
        """
        for field in [ 'a', '#', 'Z', '5' ]:
            with self.subTest(field):
                invalid_struct = self.teststruct + [('invalid', field)]
                with self.assertRaises(struct.error, msg='bad char in struct format'):
                    ns.NamedStruct('test', invalid_struct)

    def test_init_empty_struct(self):
        """Test an empty NamedStruct."""

        val = ns.NamedStruct('test', [])
        self.assertEqual(val._tuple._fields, ())  # pylint: disable=W0212
        # default mode is 'Native', or '='
        self.assertEqual(val._struct.format, b'=')  # pylint: disable=W0212

    def test_modes(self):
        """Test all valid NamedStruct modes."""

        testfields = ['a', 'b', 'c']
        testtuple = collections.namedtuple('test', testfields)
        for mode in modes.Mode:
            with self.subTest(mode):
                val = ns.NamedStruct('test', self.teststruct, mode)
                self.assertEqual(val._tuple._fields, tuple(testfields))  # pylint: disable=W0212
                fmt = '{}b3xHx10sx'.format(mode.value)
                self.assertEqual(val._struct.format, fmt.encode())  # pylint: disable=W0212
                self.assertIsNot(val._tuple, testtuple)  # pylint: disable=W0212
                self.assertEqual(val._tuple._fields, testtuple._fields)  # pylint: disable=W0212
                self.assertEqual(val.size(), 18)

    @unittest.skip('pack test not implemented')
    def test_pack(self):
        """Test packing data for all NamedStruct formats."""

        # TODO: pick at least 3 values for every field and verify that they can
        # be packed in a variety of modes
        # _pack_from_tuple()
        # pack()
        # pack_into()
        self.fail('not implemented')

    @unittest.skip('unpack test not implemented')
    def test_unpack(self):
        """Test unpacking data for all NamedStruct formats."""

        # TODO: pick at least 3 values for every field and verify that they can
        # be unpacked in a variety of modes
        # unpack()
        # unpack_from()
        self.fail('not implemented')
