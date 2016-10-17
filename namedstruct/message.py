"""StarStruct class."""

import collections
import struct
import starstruct.modes
from starstruct.element import Element


# pylint: disable=line-too-long
class Message(object):
    """An object much like NamedTuple, but with additional formatting."""

    # pylint: disable=too-many-branches
    def __init__(self, name, fields, mode=starstruct.modes.Mode.Native, alignment=1):
        """
        Initialize a StarStruct object.

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
        self.mode = mode
        self.alignment = alignment

        # The structure definition must be a list of
        #   ('name', 'format', <optional>)
        # tuples
        if not isinstance(fields, list) \
                or not all(isinstance(x, tuple) for x in fields):
            raise TypeError('invalid fields: {}'.format(fields))

        if not isinstance(mode, starstruct.modes.Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # Create an ordered dictionary (so element order is preserved) out of
        # the individual message fields.  Ensure that there are no duplicate
        # field names.
        self._elements = collections.OrderedDict()
        for field in fields:
            if field[0] not in self._elements:
                if isinstance(field[0], str):
                    self._elements[field[0]] = Element.factory(field, mode, alignment)
                elif isinstance(field[0], bytes):
                    self._elements[field[0].decode('utf-8')] = Element.factory(field, mode, alignment)
                else:
                    raise NotImplementedError
            else:
                raise TypeError('duplicate field {} in {}'.format(field[0], fields))

        # Validate all of the elements of this message
        for elem in self._elements.values():
            elem.validate(self._elements)

        # Now that the format has been validated, create a named tuple with the
        # correct fields.
        named_fields = [elem.name for elem in self._elements.values() if elem.name]
        self._tuple = collections.namedtuple(self.name, named_fields)

    def update(self, mode=None, alignment=None):
        """ Change the mode of a message. """
        if mode and not isinstance(mode, starstruct.modes.Mode):
            raise TypeError('invalid mode: {}'.format(mode))

        # Change the mode for all elements
        for key in self._elements.keys():
            self._elements[key].update(mode, alignment)

    def is_unpacked(self, other):
        """
        Provide a function that allows checking if an unpacked message tuple
        is an instance of what could be unpacked from a particular message
        object.
        """
        # First check to see if the passed in object is a namedtuple
        # that matches this message type
        if not isinstance(other, self._tuple):
            return False

        # Then check any element values that may be another message type to
        # ensure that the sub-elements are valid types.
        for key in self._elements.keys():
            if hasattr(self._elements[key].format, 'is_unpacked'):
                # If the format for an element is Message object (that has the
                # is_unpacked() function defined), call the is_unpacked()
                # function.
                msg = self._elements[key].format
                if not msg.is_unpacked(getattr(other, key)):
                    return False
            if hasattr(self._elements[key].format, 'keys'):
                # If the format for an element is a dictionary, attempt to
                # extract the correct item with the assumption that the ref
                # attribute identifies the discriminator

                # Select the correct message object based on the value of the
                # referenced item
                ref_val = getattr(other, self._elements[key].ref)
                if ref_val not in self._elements[key].format.keys():
                    return False
                msg = self._elements[key].format[ref_val]
                if not msg.is_unpacked(getattr(other, key)):
                    return False
        return True

    def pack(self, obj=None, **kwargs):
        """Pack the provided values using the initialized format."""
        # Handle a positional dictionary argument as well as the more generic kwargs
        if obj and isinstance(obj, dict):
            kwargs = obj
        return b''.join([elem.pack(kwargs) for elem in self._elements.values()])

    def unpack_partial(self, buf):
        """
        Unpack a partial message from a buffer.

        This doesn't re-use the "unpack_from" function name from the struct
        module because the parameters and return values are not consistent
        between this function and the struct module.
        """
        msg = self._tuple._make([None] * len(self._tuple._fields))
        for elem in self._elements.values():
            (val, unused) = elem.unpack(msg, buf)
            buf = unused
            # Update the unpacked message with all non-padding elements
            if elem.name:
                msg = msg._replace(**dict([(elem.name, val)]))
        return (msg, buf)

    def unpack(self, buf):
        """Unpack the buffer using the initialized format."""
        (msg, unused) = self.unpack_partial(buf)
        if unused:
            error = 'buffer not fully used by unpack: {}'.format(unused)
            raise ValueError(error)
        return msg

    def make(self, obj=None, **kwargs):
        """
        A utility function that returns a namedtuple based on the current
        object's format for the supplied object.
        """
        if obj is not None:
            if isinstance(obj, dict):
                kwargs = obj
            elif isinstance(obj, tuple):
                kwargs = obj._asdict()
        msg = self._tuple._make([None] * len(self._tuple._fields))
        # Only attempt to "make" fields that are in the tuple
        for field in self._tuple._fields:
            val = self._elements[field].make(kwargs)
            msg = msg._replace(**dict([(field, val)]))
        return msg

    def __len__(self):
        if self._elements == {}:
            return 0

        size = 0
        for val in self._elements.values():
            if isinstance(val.format, (bytes, str)):
                size += struct.calcsize(val.format)
            elif isinstance(val.format, (dict, )):
                lengths = {len(item) for item in val.format.values()}
                if len(lengths) > 1:
                    raise AttributeError('Unable to calculate size due to differing size sub items')

                size += sum(lengths)
            else:
                size += len(val.format)

        return size
