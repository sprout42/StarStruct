[![Build Status](https://travis-ci.org/sprout42/StarStruct.svg?branch=master)](https://travis-ci.org/sprout42/StarStruct)
[![Coverage Status](https://coveralls.io/repos/github/sprout42/StarStruct/badge.svg?branch=master)](https://coveralls.io/github/sprout42/StarStruct?branch=master)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/sprout42/StarStruct/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/sprout42/StarStruct/?branch=master)

StarStruct
======
A package that provides consistent packing and unpacking of binary data

Getting Started
===============

Requirements
------------

* Python 3.5+

Installation
------------

StarStruct can be installed with pip:

```
$ pip install starstruct
```

or directly from the source code:

```
$ git clone https://github.com/sprout42/StarStruct.git
$ cd StarStruct
$ python setup.py install
```

Basic Usage
===========

After installation, the package can imported:

```
$ python
>>> import starstruct
>>> starstruct.__version__
```

An example of the package can be seen below

```python
import enum

# Import the package
from starstruct import Mode
from starstruct.message import Message

# A custom Enum you might be using
class MyEnum(enum.Enum):
    my_custom_data_type = 0x0
    my_other_data_type = 0x1
    final_data_type = 0x2

SizeOfData = Message('Data', [('pad', '8x')], Mode.Big)
AnotherDataSize = Message('Data', [
    ('status', 'H'),
    ('pad', '6x'),
], Mode.Big)

# Create your Message
MyMessage = Message('message_name', [
    ('an_important_integer', 'i'),                    # Pack it into the size of a struct integer
    ('ten_long_string', '10s'),                       # Pack it like 10 consecutive characters
    ('a_fixed_point_number', 'F', 'i', 4),            # Pack it in the size of an integer, but with four bits of precision
                                                      # as a floating point number
    ('union_identifier', 'B', MyEnum),
    ('like_a_c_union', {
        MyEnum.my_custom_data_type: SizeOfData,       # These sizes should usually all be the same,
        MyEnum.my_other_data_type: AnotherDataSize,   # but they can be of different styles!
        MyEnum.final_data_type: SizeOfData,
    }, 'union_identifier'),                           # Choose which type of thing based on union_identifier
], Mode.Big)                                          # Pack it with big endianess

# Now you can use a dictionary to make your messages
data_1 = {
    'an_important_integer': 42,
    'ten_long_string': 'wow! stuff',
    'a_fixed_point_number': '1.25',
    'union_identifier': MyEnum.my_other_data_type,
    'like_a_c_union': {'status': 1}
}

named_tuple_version = MyMessage.make(data_1)
print(named_tuple_version.an_important_integer)  # 42
print(named_tuple_version.a_fixed_point_number)  # b'\x00\x00\x00\x14'

packed_message = MyMessage.pack(data_1)
print(packed_message)  # b'\x00\x00\x00*wow! stuff\x00\x00\x00\x14\x01\x00\x01\x00\x00\x00\x00\x00\x00'

unpacked_message = MyMessage.unpack(packed_message)
print(unpacked_message.an_important_integer)  # 42
print(unpacked_message.a_fixed_point_number)  # 1.25

# -----------------------
# Variable sized messages
# -----------------------

RepeatedMessage = Message('Repeated', [
    ('x', 'B'),
    ('y', 'H'),
])

VariableMessage = Message('variable_message', [
    ('length_in_objects', 'H', 'message_data'),             # length field, in terms of message objects
    ('message_data', RepeatedMessage, 'length_in_objects'),  # variable message length data
    (b'length_in_bytes', 'B', 'bytes_data'),                # length field, in terms of packed bytes
    ('bytes_data', RepeatedMessage, b'length_in_bytes'),    # variable bytes length data
    ('repeated_data', RepeatedMessage, 3),                  # fixed length repeated message
], Mode.Little)

variable_data = {
    'length_in_objects': 2,  # Two objects long
    'message_data': [
        {'x': 5, 'y': 6},    # Object number 1
        {'x': 9, 'y': 1},    # Object number 2
    ],
    'length_in_bytes': 12,    # Each object is 3 bytes long, so 4 objects
    'bytes_data': [
        {'x': 0, 'y': 8},    # Object number 1, bytes 0 - 2
        {'x': 1, 'y': 9},    # Object number 2, bytes 3 - 5
        {'x': 2, 'y': 0},    # Object number 3, bytes 6 - 8
        {'x': 6, 'y': 2},    # Object number 4, bytes 9 - 11
    ],
    'repeated_data': [       # No length field specified required. Just the messages
        {'x': 1, 'y': 9},
        {'x': 1, 'y': 9},
        {'x': 0, 'y': 5},
    ],
}

named_tuple_version = VariableMessage.make(variable_data)
print(named_tuple_version.length_in_objects)               # 2
print(named_tuple_version.length_in_bytes)                 # 12
print(named_tuple_version.bytes_data)                      # [Repeated(x=0, y=8),
                                                           # Repeated(x=1, y=9),
                                                           # Repeated(x=2, y=0),
                                                           # Repeated(x=6, y=2)]

packed_message = VariableMessage.pack(**variable_data)
print(packed_message)                                      # b' x02 x00 x05 x06 x00 t x01 x00 \
                                                           # x0c x00 x08 x00 x01 t x00 x02 \
                                                           # x00 x00 x06 x02 x00 x01 t x00 \
                                                           # x01 t x00 x00 x05 x00'

unpacked_message = VariableMessage.unpack(packed_message)
print(unpacked_mesage.length_in_objects)                   # 2
print(unpacked_mesage.length_in_bytes)                     # 12
print(unpacked_mesage.bytes_data)                          # [Repeated(x=0, y=8),
                                                           # Repeated(x=1, y=9),
                                                           # Repeated(x=2, y=0),
                                                           # Repeated(x=6, y=2)]

```
