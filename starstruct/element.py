"""StarStruct element class."""

from typing import Optional, Tuple

from starstruct.modes import Mode


def register(cls):
    """ A handy decorator to register a class as an element """
    Element.register(cls)
    return cls


class Element(object):
    """
    A class factory that determines the type of the field passed in, and
    instantiates the correct class type.
    """
    elementtypes = []

    @classmethod
    def register(cls, element):
        """Function used to register new element subclasses."""
        cls.elementtypes.append(element)

    @classmethod
    def factory(cls, field: tuple, mode: Optional[Mode]=Mode.Native, alignment: Optional[int]=1):
        """
        Initialize a StarStruct element object based on the type of element
        parameters provided.


        Where the values in the tuple determine the type of element.

        These are the possible element types:
         1. Normal (base): a standard python struct format character, and a
            field name are provided.  The optional element should not provided.

         2. Enum: a standard python struct format character and field name are
            provided, but the 3rd optional element is provided which is a
            subclass of enum.Enum.

         3. Length: a standard python struct format character that represents
            an unsigned numeric value, and the field name are provided, but the
            3rd optional element is provided and is a string.  In this case the
            string is assumed to be another field which is the name of a
            Variable element.

         4. Variable: a variable length element that accommodates 0 or more of
            another StarStruct.message.  The format field should be a valid
            StarStruct.message, the optional 3rd element must be provided and
            should be the name of a valid Length element or an int.  The
            validity of the referenced element must be checked after the
            creation of the entire message with the Message.validate() function.

         5. Discriminated: a message element that can have multiple formats
            such as a C union.  The format field should be a dictionary where
            the keys represent values of a referenced enumeration field, and
            the value for each entry is a valid StarStruct.message, or None.
            The optional 3rd element must be provided and should be the name of
            a valid Enum element.  The validity of the referenced element must
            be checked after the creation of the entire message with the
            Message.validate() function.


        :param field: The field must be a tuple of the following form::

            (name, format, <optional>)

        :param mode: The mode in which to pack the information.
        :param alignment: The number of bytes to align objects with.
        :returns: An element whose fields match those passed in
        """

        if not isinstance(mode, Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # The field parameter is a single field tuple:
        #   ('name', 'format', <optional>)
        if not isinstance(field, tuple):
            raise TypeError('invalid element: {}'.format(field))

        # The name of the element must be a non-null string or bytes
        # provided in as the first part of the field tuple
        if not field[0] or not isinstance(field[0], (str, bytes)):
            raise TypeError('invalid name: {}'.format(field[0]))

        valid_elems = []
        for elem in cls.elementtypes:
            try:
                if elem.valid(field):
                    valid_elems.append(elem)
            except (TypeError, KeyError):
                continue

        if len(valid_elems) > 1:
            raise ValueError('More than one elemn was valid.\n\tField: {0}\n\tElems: {1}'.format(
                field, valid_elems))
        elif len(valid_elems) == 1:
            return valid_elems[0](field, mode, alignment)

        # If the function made it this far, the field specification is not valid
        raise TypeError('invalid field: {}'.format(field))

    @staticmethod
    def valid(field: tuple) -> bool:
        """
        Require element objects to implement this abstract function.

        Validation function to determine if a field tuple represents a valid
        element type.

        The basics have already been validated by the Element factory class,
        validate that the struct format is a valid numeric value.

        :param field: The format specifier for an element
        :returns: Whether this field tuple is valid for this class.
        """
        raise NotImplementedError

    def validate(self, msg: dict) -> bool:
        """
        Require element objects to implement this function.

        :param msg: The current values passed in to the element
        :returns: Whether this message represents a valid element.
        """
        raise NotImplementedError

    def update(self, mode: Mode, alignment: int) -> None:
        """
        Require element objects to implement this function.

        :param mode: The new mode for the Element
        :param alignment: The new alignment for the element
        """
        raise NotImplementedError

    def pack(self, msg: dict) -> bytes:
        """
        Require element objects to implement this function.

        :param msg: The values to pack into bytes
        :returns: The msg packed into bytes as specified by the format
        """
        raise NotImplementedError

    def unpack(self, msg: dict, buf: bytes) -> Tuple[dict, bytes]:
        """
        Require element objects to implement this function.

        :param msg: The values unpacked thus far from the bytes
        :param buf: The remaining bytes to unpack
        :returns: The updated message and the remaining bytes
        """
        raise NotImplementedError

    def make(self, msg: dict):
        """
        Require element objects to implement this function.

        :param msg: The values to place into the named tuple object

        :todo: How do I specify the correct type for this?
        """
        raise NotImplementedError
