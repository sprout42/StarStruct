"""binary representation modes used for a StarStruct object."""

import sys
import enum


@enum.unique
class Mode(enum.Enum):
    """The StarStruct modes match the modes supported by struct.pack/unpack."""
    Native = '='
    Little = '<'
    Big = '>'
    Network = '!'

    def to_byteorder(self):
        """
        Convert a Mode to a byteorder string such as required by the
        to_bytes() or from_bytes() functions.
        """
        if self == self.Native:
            return sys.byteorder
        elif self == self.Little:
            return 'little'
        else:  # Big or Network
            return 'big'

    @staticmethod
    def from_byteorder(val):
        """
        Convert a byteorder string such as used by the to_bytes() or
        from_bytes() functions into a Mode value.
        """
        if val == 'little':
            return Mode.Little
        elif val == 'big':
            return Mode.Big
        elif val == 'native':  # custom
            return Mode.Native
        elif val == 'network':  # custom
            return Mode.Network
        raise TypeError('{} not a valid byteorder'.format(val))
