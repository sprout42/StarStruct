import re


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

    def __repr__(self):
        return 'BitField({})'.format(self.enum)

    def __str__(self):
        return 'BitField({})'.format(self.enum)

    def pack(self, arg):
        """
        Take a list (or single value) and bitwise-or all the values together
        """
        if arg:
            # Handle a variety of inputs: list or single, enum or raw
            if isinstance(arg, list):
                arg_list = arg
            else:
                arg_list = [arg]

            # To make usage a bit nice/easier if the elements of the list
            # are strings assume that they are enum names and attempt to
            # convert them to the correct enumeration values.
            value = 0
            for item in arg_list:
                if isinstance(item, self.enum):
                    value |= item.value
                elif isinstance(item, str):
                    try:
                        value |= getattr(self.enum, item).value
                    except AttributeError:
                        enum_name = re.match(r"<enum '(\S+)'>", str(self.enum)).group(1)
                        msg = '{} is not a valid {}'.format(item, enum_name)
                        raise ValueError(msg)
                else:
                    # Assume that the item is an integer value, convert it to
                    # an enum value to ensure it is a valid value for this
                    # bitfield.
                    value |= self.enum(item).value

            return value
        else:
            return 0

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
