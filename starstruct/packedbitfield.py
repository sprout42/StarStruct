import re
import collections
import functools
import starstruct.bitfield


class PackedBitField(object):
    """
    A class that is used to bitwise pack/unpack one or more enumerations or
    bitfields to/from an integer value
    """
    def __init__(self, *args):
        # Ensure that there are no duplicate enum or bitfield types in the list
        member_bitfields = (k for k in args if isinstance(k, starstruct.bitfield.BitField))
        all_enums = args + tuple(b.enum for b in member_bitfields)
        if len(all_enums) != len(set(all_enums)):
            msg = 'Duplicate fields not allowed: {}'.format(args)
            raise TypeError(msg)

        # Ensure that all fields are either bitfields, or enums with all
        # members of each enumeration type are integers
        member_enums = (k for k in args if not isinstance(k, starstruct.bitfield.BitField))
        for key in member_enums:
            if not all(isinstance(member.value, int) for member in key):
                msg = 'Enum {} members must have integer values'.format(repr(key))
                raise TypeError(msg)

        # Allow enum to be a list of enumerations that need bitpacked sequentially
        self._fields = collections.OrderedDict(zip(args, [{}] * len(args)))

        # Determine the bits required for the enumeration so they can all be
        # packed correctly.  Assume that the furthest right enumeration should
        # have a bit offset of 0.
        total_width = 0
        for key in reversed(self._fields):
            if isinstance(key, starstruct.bitfield.BitField):
                all_bits = key.bit_mask
            else:
                all_bits = functools.reduce(lambda x, y: x | y, [k.value for k in key])

            self._fields[key] = {
                'offset': total_width,
                'mask': all_bits << total_width,
                'width': all_bits.bit_length(),
            }

            total_width += self._fields[key]['width']

        # Track the bit mask and bit length attributes just like BitField
        self.bit_mask = functools.reduce(lambda x, y: x | y, [v['mask'] for v in self._fields.values()])
        self.bit_length = total_width

    def __repr__(self):
        return 'PackedBitField({})'.format(list(self._fields))

    def __str__(self):
        return 'PackedBitField({})'.format(list(self._fields))

    def find_value(self, item):
        """
        Take a value, determine if it matches one, and only one, of the member fields
        """
        # pylint: disable=too-many-branches

        # Split the member fields into bitfields and enums
        member_enums = [k for k in self._fields if not isinstance(k, starstruct.bitfield.BitField)]
        member_bitfields = [k for k in self._fields if isinstance(k, starstruct.bitfield.BitField)]

        # See if the supplied value is an enum or bitfield value
        matches = []
        for key in member_bitfields:
            try:
                matches.append((key.find_value(item), key))
            except ValueError:
                # This just means it isn't a member of this bitfield
                pass

        # Also check for matches in the enums.  This helps guard against
        # ambiguous inputs where the bitfield and enum types overlap.
        if isinstance(item, tuple(member_enums)):
            for key in member_enums:
                if isinstance(item, key):
                    # This is guaranteed a unique match, so return now
                    return (item, key)
        elif isinstance(item, str):
            # If it's a string, then check it against the enum fields
            # (bitfields should already have been validated)
            for key in member_enums:
                try:
                    matches.append((getattr(key, item), key))
                except AttributeError:
                    # This is the normal error to throw if the enum name is
                    # not valid for this enumeration type.  Check the next enum.
                    pass
        else:
            # Lastly, assume that the item is an integer value, attempt to
            # convert it to one of the enum values to ensure it is a valid
            # value.  But if it matches more than one member field, we are
            # unable to pack this properly.
            for key in member_enums:
                try:
                    matches.append((key(item), key))
                except ValueError:
                    # This just means that the value is not valid for a
                    # specific enum type, check all enums for a match before
                    # raising a ValueError
                    pass

        if len(matches) == 1:
            return matches[0]
        elif len(matches) < 1:
            msg = '{} is not a valid {}'.format(item, list(self._fields))
            raise ValueError(msg)
        elif len(matches) > 1:
            msg = '{} is not a unique {}'.format(item, list(self._fields))
            raise ValueError(msg)

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
                (enum_val, key) = self.find_value(item)
                value |= (enum_val.value << self._fields[key]['offset'])

        return value

    def unpack(self, val):
        """
        Take a single number and split it out into all values that are present
        """
        values = []
        for key in self._fields:
            enum_specific_bits = (val & self._fields[key]['mask']) >> self._fields[key]['offset']
            if isinstance(key, starstruct.bitfield.BitField):
                values.extend(key.unpack(enum_specific_bits))
            else:
                try:
                    values.append(key(enum_specific_bits))
                except ValueError:
                    enum_name = re.match(r"<enum '(\S+)'>", str(key)).group(1)
                    msg = '{} is not a valid {}'.format(enum_specific_bits, enum_name)
                    raise ValueError(msg)
        return frozenset(values)

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
                values.append(self.find_value(item)[0])

        # return this list as a frozenset
        return frozenset(values)
