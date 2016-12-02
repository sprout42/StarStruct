
import collections


def StarTuple(name, named_fields, elements):
    named_tuple = collections.namedtuple(name, named_fields)

    def this_pack(self):
        packed = bytes()
        for key, value in self.__elements.items():
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
    named_tuple.__elements = elements

    return named_tuple
