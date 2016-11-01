
import collections


# print(type(collections.namedtuple))

# for item in dir(collections.namedtuple):
#     print(item, getattr(collections.namedtuple, item))


def StarTuple(name, named_fields, elements):
    named_tuple = collections.namedtuple(name, named_fields)

    def this_pack(self):
        packed = bytes()
        for key, value in self.__elements.items():
            packed += value.pack(self._asdict())

        return packed

    named_tuple.pack = this_pack
    named_tuple.__elements = elements

    return named_tuple
