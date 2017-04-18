#!/usr/bin/python3

import struct

# packing
simple_string = 'artur'
encoded_string = simple_string.encode('utf-8')
struct_pack_format = '<H{}s'.format(len(encoded_string))
packed_struct = struct.pack(struct_pack_format, len(encoded_string), encoded_string)
print(packed_struct)

#unpacking
len_format = struct.Struct('<H')
len_str = len_format.unpack(packed_struct[:len_format.size])[0]
str_format = '{}s'.format(len_str)
unpacked_string = struct.unpack(str_format, packed_struct[len_format.size:])
print(unpacked_string[0].decode('utf-8'))