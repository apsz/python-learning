#!/usr/bin/python3

import struct

a = list(range(10))
size = struct.pack('<I', len(a))
print(struct.unpack('<I', size)[0])