"""Tests for the starstruct class"""

# import pytest

from starstruct.message import Message
# from starstruct.modes import Mode


# pylint: disable=line-too-long,invalid-name
class TestStarStruct:
    """StarStruct module tests"""

    Repeated = Message('Repeated', [
        ('x', 'B'),
        ('y', 'B'),
        ('z', 'H'),
    ])

    def test_escape_sequence_items(self):
        TestStruct = Message('TestStruct', [
            ('escaped_data', self.Repeated, {
                'escape': {
                    'start': b'\xff\x00\xff\x11',
                    'separator': b'\x12\x12',
                    'end': b'\x11\xff\x00\xff',
                },
            }),
        ])

        test_data = {
            'escaped_data': [
                {'x': 7, 'y': 9, 'z': 13},
                {'x': 2, 'y': 8, 'z': 27},
                {'x': 6, 'y': 7, 'z': 11},
            ],
        }

        made = TestStruct.make(test_data)
        assert made.escaped_data[0].x == 7
        assert made.escaped_data[0].y == 9

        packed = TestStruct.pack(test_data)

        unpacked = TestStruct.unpack(packed)
        assert unpacked == made
