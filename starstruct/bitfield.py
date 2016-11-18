import functools


class BitField(object):
    def __init__(self, enum):
        if not all(isinstance(member.value, int) for member in enum):
            msg = 'Enum {} members must have integer values'.format(repr(enum))
            raise TypeError(msg)
        self.enum = enum

    def __repr__(self):
        return 'BitField({})'.format(self.enum)

    def __str__(self):
        return 'BitField({})'.format(self.enum)

    def pack(self, arg):
        """
        Take a list (or single value) and bitwise-or all the values together
        """
        # Handle a variety of inputs: list or single, enum or raw
        if isinstance(arg, list):
            values = [self.enum(value) for value in arg]
        else:
            values = [self.enum(arg)]

        # left side is an integer, right side is an enum value
        return functools.reduce(lambda x, y: x | y.value, values, 0)

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
        # Handle the same inputs as the pack function
        if isinstance(arg, list):
            values = [self.enum(value) for value in arg]
        else:
            values = [self.enum(arg)]

        # return this list as a frozenset
        return frozenset(values)
