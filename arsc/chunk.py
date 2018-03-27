#!/usr/bin/env python3
## \file chunk.py
# \brief ResChunk and related
import unittest
from arsc.type.uint16 import uint16
from arsc.type.uint32 import uint32
from arsc.types import ResourceType

## \class ResChunk_header
# \brief Header that appears at the front of every data chunk in a resource.
class ResChunk_header:

    ResChunk_header_len = len(ResourceType.RES_NULL_TYPE) + len(uint16(0)) + \
            len(uint32(0))

    def __init__(self, chunkType=ResourceType.RES_NULL_TYPE,
            headerSize=ResChunk_header_len, size=ResChunk_header_len):
        if isinstance(chunkType, ResourceType):
            self.type = chunkType
        else:
            self.type = ResourceType(chunkType, little=True)

        if isinstance(headerSize, uint16):
            self.headerSize = headerSize
        else:
            self.headerSize = uint16(headerSize, little=True)

        if isinstance(size, uint32):
            self.size = size
        else:
            self.size = uint32(size, little=True)

    def __str__(self):
        return '{{type={type}, headerSize={headerSize}, size={size}}}'.format(
                type=str(self.type), headerSize=self.headerSize, size=self.size)

    def __repr__(self):
        return '{c}({type}, {headerSize}, {size})'.format(c=type(self).__name__,
                type=str(self.type), headerSize=self.headerSize, size=self.size)

    def __eq__(self, rhs):
        return self.type == rhs.type and self.headerSize == rhs.headerSize and \
                self.size == rhs.size

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        chunkType = bytes(reversed(bytes(self.type))) # always little
        headerSize = bytes(self.headerSize)
        size = bytes(self.size)
        return chunkType + headerSize + size

    def from_bytes(b, little=True):
        chunkType, b = ResourceType.from_bytes(b, little=True)
        headerSize, b = uint16.from_bytes(b, little=True)
        size, b = uint32.from_bytes(b, little=True)
        return ResChunk_header(chunkType, headerSize, size), b

class ResChunk_headerTests(unittest.TestCase):

    def test_bytes(self):
        invector = ResChunk_header(ResourceType.RES_TABLE_TYPE, 0xc, 0x1a3ac)
        expected = b'\2\0\x0c\0\xac\xa3\x01\0'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\2\0\x0c\0\xac\xa3\x01\0\x13\x37'
        expObj, expBuf = ResChunk_header(ResourceType.RES_TABLE_TYPE, 0xc, 0x1a3ac), b'\x13\x37'
        actObj, actBuf = ResChunk_header.from_bytes(invector)

        self.assertEqual(expObj, actObj)
        self.assertEqual(expBuf, actBuf)

    def test_len(self):
        invector = ResChunk_header(ResourceType.RES_TABLE_TYPE, 0xc, 0x1a3ac)
        expected = 8
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = ResChunk_header(ResourceType.RES_TABLE_TYPE, 0xc, 0x1a3ac)
        expected = '{type=ResourceType.RES_TABLE_TYPE, headerSize=12, size=107436}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResChunk_header(ResourceType.RES_TABLE_TYPE, 0xc, 0x1a3ac)
        expected = 'ResChunk_header(ResourceType.RES_TABLE_TYPE, 12, 107436)'
        actual = repr(invector)

        self.assertEqual(expected, actual)
