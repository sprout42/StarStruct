"""NamedStruct element class."""

import namedstruct


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
    def factory(cls, field, mode=namedstruct.modes.Mode.Native):
        """
        Initialize a NamedStruct element object based on the type of element
        parameters provided.

        The field must be a tuple of the following form:
            (name, format, <optional>)

        Where the values in the tuple determine the type of element.

        These are the possible element types:
         1. Normal (base): a standard python struct format character, and a
            field name are provided.  The optional element should not provided.

         2. Enum: a standard python struct format character and field name are
            provided, but the 3rd optional element is provided which is a
            subclass of enum.Enum.

         3. Length: a standard python struct format character that represents a
            numeric value, and the field name are provided, but the 3rd
            optional element is provided and is a string.  In this case the
            string is assumed to be another field which is the name of a
            Variable element.

         4. Variable: a variable length element that accommodates 0 or more of
            another NamedStruct.message.  The format field should be a valid
            NamedStruct.message, the optional 3rd element must be provided and
            should be the name of a valid Length element.  The validity of the
            referenced element must be checked after the creation of the entire
            message with the Element.validate() function.

         5. Discriminated: a message element that can have multiple formats
            such as a C union.  The format field should be a dictionary where
            the keys represent values of a referenced enumeration field, and
            the value for each entry is a valid NamedStruct.message.  The
            optional 3rd element must be provided and should be the name of a
            valid Enum element.  The validity of the referenced element must
            be checked after the creation of the entire message with the
            Element.validate() function.
        """

        if not isinstance(mode, namedstruct.modes.Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # The field parameter is a single field tuple:
        #   ('name', 'format')
        if not isinstance(field, tuple):
            raise TypeError('invalid element: {}'.format(field))

        # The name of the element must be a non-null string provided in as the
        # first part of the field tuple
        if not field[0] or not isinstance(field[0], str):
            raise TypeError('invalid name: {}'.format(field[0]))

        for elem in cls.elementtypes:
            if elem.valid(field):
                return elem(field, mode)

        # If the function made it this far, the field specification is not valid
        raise TypeError('invalid field: {}'.format(field))

    @staticmethod
    def valid(field):
        """Require element objects to implement this function."""
        raise NotImplementedError

    def pack(self, msg):
        """Require element objects to implement this function."""
        raise NotImplementedError

    def unpack(self, msg, buf):
        """Require element objects to implement this function."""
        raise NotImplementedError
