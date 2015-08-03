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
        ('e', 'L'),     # unsigned long: 0, 2^32-1
    ]

    testvalues = [
        { 'a': -128, 'b': 0,     'c': b'0123456789',        'e': 0 },
        { 'a': 127,  'b': 65535, 'c': b'abcdefghij',        'e': 0xFFFFFFFF },
        { 'a': -1,   'b': 32767, 'c': b'\n\tzyx\0\0\0\0\0', 'e': 0x7FFFFFFF },
        { 'a': 100,  'b': 100,   'c': b'a0b1c2d3e4',        'e': 10000 },
    ]

    testbytes = {
        'little': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF',
            b'\xFF\x00\x00\x00\xFF\x7F\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\x7F',
            b'\x64\x00\x00\x00\x64\x00\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x10\x27\x00\x00',
        ],
        'big': [
            b'\x80\x00\x00\x00\x00\x00\x00\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x00\x00\x00\x00\x00',
            b'\x7F\x00\x00\x00\xFF\xFF\x00\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x00\xFF\xFF\xFF\xFF',
            b'\xFF\x00\x00\x00\x7F\xFF\x00\x0A\x09\x7A\x79\x78\x00\x00\x00\x00\x00\x00\x7F\xFF\xFF\xFF',
            b'\x64\x00\x00\x00\x00\x64\x00\x61\x30\x62\x31\x63\x32\x64\x33\x65\x34\x00\x00\x00\x27\x10',
        ],
    }

    def test_init_invalid_name(self):
        """Test invalid NamedStruct names."""

        for name in [None, '', 1, dict(), list()]:
            with self.subTest(name):
                with self.assertRaises(TypeError) as cm:
                    ns.NamedStruct(name, self.teststruct)
                self.assertEqual(str(cm.exception), 'invalid name: {}'.format(name))

    def test_init_invalid_mode(self):
        """Test invalid NamedStruct modes."""

        for mode in ['=', 'stuff', 0, -1, 1]:
            with self.subTest(mode):
                with self.assertRaises(TypeError) as cm:
                    ns.NamedStruct('test', self.teststruct, mode)
                self.assertEqual(str(cm.exception), 'invalid mode: {}'.format(mode))

    def test_init_invalid_struct_format(self):
        """Test invalid NamedStruct format fields."""

        """
        Invalid fields are format specifiers that are not accepted by the
        Struct class.  Valid fields are identified in here:
        https://docs.python.org/3/library/ns.html#format-characters

        Append the invalid field to the end of the standard test structure and
        ensure it fails.
        """
        for field in [ 'a', '#', 'Z' ]:
            with self.subTest(field):
                invalid_struct = self.teststruct + [('invalid', field)]
                with self.assertRaises(struct.error) as cm:
                    ns.NamedStruct('test', invalid_struct)
                self.assertEqual(str(cm.exception), 'bad char in struct format')

        """
        Test invalid characters and an invalid trailing number.
        """
        field = '5'
        with self.subTest('5'):
            invalid_struct = self.teststruct + [('invalid', field)]
            with self.assertRaises(struct.error) as cm:
                ns.NamedStruct('test', invalid_struct)
            self.assertEqual(str(cm.exception), 'repeat count given without format specifier')

    @unittest.skip('invalid tuple field not implemented')
    def test_init_invalid_field(self):
        """Test invalid field tuple detection."""

        self.fail('not implemented')

    def test_init_empty_struct(self):
        """Test an empty NamedStruct."""

        val = ns.NamedStruct('test', [])
        self.assertEqual(val._tuple._fields, ())  # pylint: disable=W0212
        # default mode is 'Native', or '='
        self.assertEqual(val._struct.format, b'=')  # pylint: disable=W0212

    def test_modes(self):
        """Test all valid NamedStruct modes."""

        testfields = ['a', 'b', 'c', 'e']
        testtuple = collections.namedtuple('test', testfields)
        for mode in modes.Mode:
            with self.subTest(mode):
                val = ns.NamedStruct('test', self.teststruct, mode)
                self.assertEqual(val._tuple._fields, tuple(testfields))  # pylint: disable=W0212
                fmt = '{}b3xHx10sxL'.format(mode.value)
                self.assertEqual(val._struct.format, fmt.encode())  # pylint: disable=W0212
                self.assertIsNot(val._tuple, testtuple)  # pylint: disable=W0212
                self.assertEqual(val._tuple._fields, testtuple._fields)  # pylint: disable=W0212
                self.assertEqual(val.size(), 22)

    def test_pack_little_endian(self):
        """Test little endian packing data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                self.assertEqual(self.testbytes['little'][idx], testobj.pack(**self.testvalues[idx]))

    def test_pack_into_little_endian(self):
        """Test little endian packing data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Little)
        import random
        import array
        # Make the test array double the required 22 bytes
        orig_buf = bytes(random.getrandbits(8) for i in range(22 * 2))
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                test_buf = array.array('B', orig_buf)

                start = idx
                end = idx + len(self.testbytes['little'][idx]) 
                expected_buf = orig_buf[:start] + self.testbytes['little'][idx] + orig_buf[end:]

                # sanity check
                result_buf = test_buf.tobytes()
                self.assertEqual(orig_buf, result_buf)
                self.assertNotEqual(expected_buf, result_buf)

                testobj.pack_into(test_buf, idx, **self.testvalues[idx])

                # actual test
                result_buf = test_buf.tobytes()
                self.assertEqual(expected_buf, result_buf)

    def test_pack_big_endian(self):
        """Test big endian packing data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Big)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                self.assertEqual(self.testbytes['big'][idx], testobj.pack(**self.testvalues[idx]))

    def test_pack_into_big_endian(self):
        """Test big endian packing data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Big)
        import random
        import array
        # Make the test array double the required 22 bytes
        orig_buf = bytes(random.getrandbits(8) for i in range(22 * 2))
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                test_buf = array.array('B', orig_buf)

                start = idx
                end = idx + len(self.testbytes['big'][idx])
                expected_buf = orig_buf[:start] + self.testbytes['big'][idx] + orig_buf[end:]

                # sanity check
                result_buf = test_buf.tobytes()
                self.assertEqual(orig_buf, result_buf)
                self.assertNotEqual(expected_buf, result_buf)

                testobj.pack_into(test_buf, idx, **self.testvalues[idx])

                # actual test
                result_buf = test_buf.tobytes()
                self.assertEqual(expected_buf, result_buf)

    def test_pack_invalid(self):
        """Test the error that occurs when attempting to pack invalid data."""

        testobj = ns.NamedStruct('test', self.teststruct)
        test_field_invalid_value = [
            ('a',               -129, 'byte format requires -128 <= number <= 127'),
            ('a',                128, 'byte format requires -128 <= number <= 127'),
            ('b',                 -1, 'ushort format requires 0 <= number <= USHRT_MAX'),
            ('b',         0xFFFF + 1, 'ushort format requires 0 <= number <= USHRT_MAX'),
            ('c', 'not a bytestring', "argument for 's' must be a bytes object"),
            ('c',                 42, "argument for 's' must be a bytes object"),
            ('e',                 -1, 'argument out of range'),
            ('e',     0xFFFFFFFF + 1, 'argument out of range'),
        ]
        for (field, value, errmsg) in test_field_invalid_value:
            sub_test_msg = '{}={}'.format(field, value)
            with self.subTest(sub_test_msg):
                # start with a valid set of values
                testvalues = self.testvalues[-1].copy()

                # Set an invalid value
                testvalues[field] = value

                with self.assertRaises(struct.error) as cm:
                    testobj.pack(**testvalues)
                self.assertEquals(str(cm.exception), errmsg)

    def test_pack_extra_fields(self):
        """Test the error that occurs when attempting to pack unexpected fields."""

        testobj = ns.NamedStruct('test', self.teststruct)
        for field in ['aa', 'd', 'invalid']:
            with self.subTest(field):
                # start with a valid set of values
                testvalues = self.testvalues[-1].copy()

                # Add an invalid field
                testvalues[field] = 42

                errmsg = "__new__() got an unexpected keyword argument '{}'".format(field)
                with self.assertRaises(TypeError) as cm:
                    testobj.pack(**testvalues)
                self.assertEquals(str(cm.exception), errmsg)

    def test_unpack_little_endian(self):
        """Test unpacking little endian data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Little)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                # returns a NamedStruct tuple
                result = testobj.unpack(self.testbytes['little'][idx])

                # convert result NamedStruct to dictionary to compare dictionary 
                # keys and values
                self.assertDictEqual(self.testvalues[idx], dict(result._asdict()))

    @unittest.skip('little endian unpack_from test not implemented')
    def test_unpack_from_little_endian(self):
        """Test unpacking little endian data for all NamedStruct formats."""

        self.fail('not implemented')

    def test_unpack_big_endian(self):
        """Test unpacking big endian data for all NamedStruct formats."""

        testobj = ns.NamedStruct('test', self.teststruct, modes.Mode.Big)
        for idx in range(len(self.testvalues)):
            with self.subTest(idx):
                # returns a NamedStruct tuple
                result = testobj.unpack(self.testbytes['big'][idx])

                # convert result NamedStruct to dictionary to compare dictionary 
                # keys and values
                self.assertDictEqual(self.testvalues[idx], dict(result._asdict()))

    @unittest.skip('big endian unpack_from test not implemented')
    def test_unpack_from_big_endian(self):
        """Test unpacking big endian data for all NamedStruct formats."""

        self.fail('not implemented')
