"""NamedStruct class."""

import collections
import namedstruct.modes
from namedstruct.element import Element

# Import the element types
from namedstruct.elementdiscriminated import ElementDiscriminated
from namedstruct.elementvariable import ElementVariable
from namedstruct.elementlength import ElementLength
from namedstruct.elementenum import ElementEnum
from namedstruct.elementpad import ElementPad
from namedstruct.elementbase import ElementBase

# Register the valid element types.  Start with the most specific checks and
# then default to the base type.
Element.register(ElementDiscriminated)
Element.register(ElementVariable)
Element.register(ElementLength)
Element.register(ElementEnum)
Element.register(ElementPad)
Element.register(ElementBase)


# pylint: disable=line-too-long
class Message(object):
    """An object much like NamedTuple, but with additional formatting."""

    # pylint: disable=too-many-branches
    def __init__(self, name, fields, mode=namedstruct.modes.Mode.Native):
        """
        Initialize a NamedStruct object.

        Creates 2 internal items, a format string which is used to call the
        struct module functions for packing and unpacking data, and a
        namedtuple instance which is used to organize the data provided to the
        pack functions and returned from the unpack functions.
        """

        # The name must be a string, this is provided to the
        # collections.namedtuple constructor when creating the namedtuple class.
        if not name or not isinstance(name, str):
            raise TypeError('invalid name: {}'.format(name))

        self.name = name

        # The structure definition must be a list of
        #   ('name', 'format', <optional>)
        # tuples
        if not isinstance(fields, list) \
                or not all(isinstance(x, tuple) for x in fields):
            raise TypeError('invalid fields: {}'.format(fields))

        if not isinstance(mode, namedstruct.modes.Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # Create an ordered dictionary (so element order is preserved) out of
        # the individual message fields.  Ensure that there are no duplicate
        # field names.
        self._elements = collections.OrderedDict()
        for field in fields:
            if field[0] not in self._elements:
                self._elements[field[0]] = Element.factory(field, mode)
            else:
                raise TypeError('duplicate field {} in {}'.format(field[0], fields))

        # Validate all of the elements of this message
        self._validate()

        # Now that the format has been validated, create a named tuple with the
        # correct fields.
        named_fields = [elem.name for elem in self._elements.values() if elem.name]
        self._tuple = collections.namedtuple(self.name, named_fields)

    def _validate(self):
        """
        A static function that validates the individual elements of a message
        against each other.

        When the individual elements are created, they are only able to be
        validated against itself, elements that reference other elements are
        unable to be validated against the existence and type of the referenced
        elements.

        The follow checks are performed:

         1. All elements that are Variable must reference valid Length elements.

         2. All Discriminated elements must reference valid Enum elements, and
            the keys of the discriminated format must be valid instances of the
            referenced Enum class.
        """
        for elem in self._elements.values():
            if isinstance(elem, namedstruct.elementlength.ElementLength):
                if not isinstance(self._elements[elem.ref], namedstruct.elementvariable.ElementVariable):
                    err = 'length field {} reference {} invalid type'
                    raise TypeError(err.format(elem.name, elem.ref))
                elif not self._elements[elem.ref].ref == elem.name:
                    err = 'length field {} reference {} mismatch'
                    raise TypeError(err.format(elem.name, elem.ref))
            elif isinstance(elem, namedstruct.elementvariable.ElementVariable):
                if not isinstance(self._elements[elem.ref], namedstruct.elementlength.ElementLength):
                    err = 'variable field {} reference {} invalid type'
                    raise TypeError(err.format(elem.name, elem.ref))
                elif not self._elements[elem.ref].ref == elem.name:
                    err = 'variable field {} reference {} mismatch'
                    raise TypeError(err.format(elem.name, elem.ref))
            elif isinstance(elem, namedstruct.elementdiscriminated.ElementDiscriminated):
                if not isinstance(self._elements[elem.ref], namedstruct.elementenum.ElementEnum):
                    err = 'discriminated field {} reference {} invalid type'
                    raise TypeError(err.format(elem.name, elem.ref))
                elif not self._elements[elem.ref].ref == elem.name:
                    err = 'discriminated field {} reference {} mismatch'
                    raise TypeError(err.format(elem.name, elem.ref))
                else:
                    for key in elem.format.keys():
                        try:
                            ref_cls = self._elements[elem.ref].ref
                            assert ref_cls(key)
                        except:
                            err = 'discriminated field {} key {} not a valid {}'
                            msg = err.format(elem.name, key, elem.ref)
                            raise TypeError(msg)

    def pack(self, **kwargs):
        """Pack the provided values using the initialized format."""
        return b''.join([elem.pack(kwargs) for elem in self._elements.values()])

    def unpack(self, buf):
        """Unpack the buffer using the initialized format."""
        msg = self._tuple._make([None] * len(self._tuple._fields))
        for elem in self._elements.values():
            (val, unused) = elem.unpack(msg, buf)
            buf = unused
            # Update the unpacked message with all non-padding elements
            if elem.name:
                msg = msg._replace(**dict([(elem.name, val)]))
        return (msg, buf)
