"""binary representation modes used for a NamedStruct object."""

import enum


@enum.unique
class Mode(enum.Enum):

    """The NamedStruct modes match the modes supported by struct.pack/unpack."""

    Native = '='
    Little = '<'
    Big = '>'
    Network = '!'
