import re
import functools


class BitField(object):
    def __init__(self, enum):
        if not all(isinstance(member.value, int) for member in enum):
            msg = 'Enum {} members must have integer values'.format(repr(enum))
            raise TypeError(msg)
        try:
            assert enum(0)
            msg = 'Cannot construct BitField from {} with a value for 0: {}'
            raise TypeError(msg.format(repr(enum), enum(0)))
        except ValueError:
            # A ValueError is raised if the enum does not have a value for 0
            pass
        self.enum = enum

        # Determine the bit mask and length for this bitfield
        self.bit_mask = functools.reduce(lambda x, y: x | y, [e.value for e in self.enum])
        self.bit_length = self.bit_mask.bit_length()

    def __repr__(self):
        return 'BitField({})'.format(self.enum)

    def __str__(self):
        return 'BitField({})'.format(self.enum)

    def find_value(self, item):
        """
        Take a value and determine the enumeration value based on value or
        enum memeber name.
        """
        # pylint: disable=too-many-branches
        if isinstance(item, str):
            # To make usage a bit nice/easier if the elements of the list are
            # strings assume that they are enum names and attempt to convert
            # them to the correct enumeration values.
            try:
                value = getattr(self.enum, item)
            except AttributeError:
                # This is the normal error to throw if the enum name is
                # not valid for this enumeration type.
                enum_name = re.match(r"<enum '(\S+)'>", str(self.enum)).group(1)
                msg = '{} is not a valid {}'.format(item, enum_name)
                raise ValueError(msg)
        elif isinstance(item, self.enum):
            value = item
        else:
            # Assume that the item is an integer value, convert it to an enum
            # value to ensure it is a valid value for this bitfield
            try:
                value = self.enum(item)
            except ValueError:
                # This value is not a valid enumeration value
                enum_name = re.match(r"<enum '(\S+)'>", str(self.enum)).group(1)
                msg = '{} is not a valid {}'.format(item, enum_name)
                raise ValueError(msg)

        return value

    def pack(self, arg):
        """
        Take a list (or single value) and bitwise-or all the values together
        """
        value = 0
        if arg is not None:
            # Handle a variety of inputs: list or single, enum or raw
            if hasattr(arg, '__iter__'):
                arg_list = arg
            else:
                arg_list = [arg]

            for item in arg_list:
                value |= self.find_value(item).value

        return value

    def unpack(self, val):
        """
        Take a single number and split it out into all values that are present
        """
        return frozenset(e for e in self.enum if e.value & val)

    def make(self, arg):
        """
        Take an input list and return a frozenset

        useful for testing
        """
        values = []
        if arg is not None:
            # Handle a variety of inputs: list or single, enum or raw
            if hasattr(arg, '__iter__'):
                arg_list = arg
            else:
                arg_list = [arg]

            for item in arg_list:
                values.append(self.find_value(item))

        # return this list as a frozenset
        return frozenset(values)
