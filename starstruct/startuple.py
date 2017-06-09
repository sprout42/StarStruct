
import collections


def StarTuple(name, named_fields, elements):
    restricted_fields = {
        # Default dunders
        '__getnewargs__',
        '__new__',
        '__slots__ ',
        '__repr__',

        # Default #oneders
        '_asdict',
        '_make',
        '_replace',

        # Fields specifier
        '_fields',

        # Startuple additions
        'pack',
        '_elements',
        '__str__',
        '_name',
    }

    intersection = restricted_fields.intersection(set(named_fields))

    if intersection:
        raise ValueError('Restricted field used. Bad fields: {0}'.format(intersection))

    named_tuple = collections.namedtuple(name, named_fields)

    # TODO: Auto update and replace!

    def this_pack(self):
        packed = bytes()
        for _, value in self._elements.items():
            packed += value.pack(self._asdict())

        return packed

    def this_str(self):
        import pprint
        fmt = 'StarTuple: <{0}>\n'.format(str(name))

        len_of_keys = 0
        for key in self._asdict().keys():
            if len(key) > len_of_keys:
                len_of_keys = len(key)

        for key, value in self._asdict().items():
            fmt += ('  {key:%d}: {value}\n' % len_of_keys).format(
                key=key,
                value=pprint.pformat(value, width=150),
            )

        return fmt

    named_tuple.pack = this_pack
    named_tuple.__str__ = this_str
    named_tuple._elements = elements
    named_tuple._name = name

    return named_tuple
