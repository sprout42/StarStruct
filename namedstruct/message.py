"""NamedStruct class."""

import collections
import namedstruct.modes
from namedstruct.element import Element

# Import the element types
from namedstruct.elementdiscriminated import ElementDiscriminated
from namedstruct.elementvariable import ElementVariable
from namedstruct.elementlength import ElementLength
from namedstruct.elementenum import ElementEnum
from namedstruct.elementstring import ElementString
from namedstruct.elementnum import ElementNum
from namedstruct.elementpad import ElementPad
from namedstruct.elementbase import ElementBase

# Register the valid element types.  Start with the most specific checks and
# then default to the base type.
Element.register(ElementDiscriminated)
Element.register(ElementVariable)
Element.register(ElementLength)
Element.register(ElementEnum)
Element.register(ElementString)
Element.register(ElementNum)
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

    def changemode(self, mode):
        """ Change the mode of a message. """
        if not isinstance(mode, namedstruct.modes.Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # Change the mode for all elements
        for key in self._elements.keys():
            self._elements[key].changemode(mode)

    def is_unpacked(self, other):
        """
        Provide a function that allows checking if an unpacked message tuple
        is an instance of what could be unpacked from a particular message
        object.
        """
        # First check to see if the passed in object is a namedtuple
        # that matches this message type
        if isinstance(other, self._tuple):
            return False

        # Then check any element values that may be another message type to
        # ensure that the sub-elements are valid types.
        for key in self._elements.keys():
            if isinstance(self._elements[key], namedstruct.elementvariable.ElementVariable):
                msg = self._elements[key].format
                if not msg.is_unpacked(getattr(other, key)):
                    return False
            elif isinstance(self._elements[key], namedstruct.elementdiscriminated.ElementDiscriminated):
                # Select the correct message object based on the value of the
                # referenced item
                ref_val = getattr(other, self._elements[key].ref)
                if ref_val not in self._elements[key].format.keys():
                    return False
                msg = self._elements[key].format[ref_val]
                if not msg.is_unpacked(getattr(other, key)):
                    return False
        return True

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
                elif not all(isinstance(key, self._elements[elem.ref].ref)
                             for key in elem.format.keys()):
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

    def pack(self, obj=None, **kwargs):
        """Pack the provided values using the initialized format."""
        # Handle a positional dictionary argument as well as the more generic kwargs
        if obj and isinstance(obj, dict):
            kwargs = obj
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

    def make(self, obj=None, **kwargs):
        """
        A utility function that returns a namedtuple based on the current
        object's format for the supplied object.
        """
        if obj and isinstance(obj, dict):
            kwargs = obj
        msg = self._tuple._make([None] * len(self._tuple._fields))
        for elem in self._elements.values():
            if isinstance(elem, ElementDiscriminated):
                val = elem.format[kwargs[elem.ref]].make(kwargs[elem.name])
                msg = msg._replace(**dict([(elem.name, val)]))
            elif isinstance(elem, ElementVariable):
                val = [elem.format.make(e) for e in kwargs[elem.name]]
                msg = msg._replace(**dict([(elem.name, val)]))
            elif isinstance(elem, (ElementLength, ElementEnum, ElementBase, ElementNum, ElementString)):
                msg = msg._replace(**dict([(elem.name, kwargs[elem.name])]))
            elif isinstance(elem, ElementPad):  # pragma: no cover (else unreachable)
                # There is no element to transform
                pass
        return msg
