#!/usr/bin/env python3
## \file stringpool.py
# \brief ResStringPool and related
import unittest
from type.uint32 import uint32
from type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.types import ResourceType

## \class ResStringPool_header
class ResStringPool_header:

    len = 28

    def __init__(self, header=None, stringCount=0, styleCount=0, flags=0,
            stringsStart=0, stylesStart=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_STRING_POOL_TYPE,
                    headerSize=ResStringPool_header.len,
                    size=ResStringPool_header.len)
        if not isinstance(header, ResChunk_header):
            raise Exception('header must be of type ResChunk_header')
        if header.type is not ResourceType.RES_STRING_POOL_TYPE:
            raise Exception('header must describe resource of type '\
                    'RES_STRING_POOL_TYPE')
        self.header = header

        if isinstance(stringCount, uint32):
            ## Number of strings in this pool (number of uint32_t indices that
            #  follow in the data).
            self.stringCount = stringCount
        else:
            self.stringCount = uint32(stringCount, little=True)

        if isinstance(styleCount, uint32):
            ## Number of style span arrays in the pool (number of uint32_t
            #  indices follow the string indices).
            self.styleCount = styleCount
        else:
            self.styleCount = uint32(styleCount, little=True)

        if isinstance(flags, uint32):
            ## Flags.
            self.flags = flags
        else:
            self.flags = uint32(flags, little=True)

        if isinstance(stringsStart, uint32):
            ## Index from header of the string data.
            self.stringsStart = stringsStart
        else:
            self.stringsStart = uint32(stringsStart, little=True)

        if isinstance(stylesStart, uint32):
            ## Index from header of the style data.
            self.stylesStart = stylesStart
        else:
            self.stylesStart = uint32(stylesStart, little=True)

    def __str__(self):
        return '{{header={header}, stringCount={stringCount}, ' \
                'styleCount={styleCount}, flags={flags}, ' \
                'stringsStart={stringsStart}, ' \
                'stylesStart={stylesStart}}}'.format(header=str(self.header),
                        stringCount=str(self.stringCount),
                        styleCount=str(self.styleCount), flags=str(self.flags),
                        stringsStart=str(self.stringsStart),
                        stylesStart=str(self.stylesStart))

    def __repr__(self):
        return '{c}({header}, {stringCount}, {styleCount}, {flags}, ' \
                '{stringsStart}, {styleCount})'.format(c=type(self).__name__,
                header=repr(self.header), stringCount=self.stringCount,
                styleCount=self.styleCount, flags=self.flags,
                stringsStart=self.stringsStart, stylesStart=self.stylesStart)

    def __eq__(self, rhs):
        return type(self) == type(rhs) and self.header == rhs.header

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        stringCount = bytes(self.stringCount)
        styleCount = bytes(self.styleCount)
        flags = bytes(self.flags)
        stringsStart = bytes(self.stringsStart)
        stylesStart = bytes(self.stylesStart)

        return header + stringCount + styleCount + flags + stringsStart + \
                stylesStart

    def from_bytes(b, little=True):
        header, b = ResChunk_header.from_bytes(b)
        stringCount, b = uint32.from_bytes(b, little=True)
        styleCount, b = uint32.from_bytes(b, little=True)
        flags, b = uint32.from_bytes(b, little=True)
        stringsStart, b = uint32.from_bytes(b, little=True)
        stylesStart, b = uint32.from_bytes(b, little=True)

        return ResStringPool_header(header, stringCount, styleCount, flags,
                stringsStart, stylesStart), b

    class Flags(Flag):
        ## If set, the string index is sorted by the string values (based on strcmp16()).
        SORTED_FLAG = 0x1
        ## String pool is encoded in UTF-8
        UTF8_FLAG = 0x100
        MAX = 0xffffffff


class ResStringPool_headerTests(unittest.TestCase):

    def test_str(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0, 0x100, 0x44,
            0)
        expected = '{header={type=ResourceType.RES_STRING_POOL_TYPE, ' \
                'headerSize=28, size=148}, stringCount=10, styleCount=0, ' \
                'flags=256, stringsStart=68, stylesStart=0}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0, 0x100, 0x44,
            0)
        expected = 'ResStringPool_header(ResChunk_header(' \
                'ResourceType.RES_STRING_POOL_TYPE, 28, 148), 10, 0, ' \
                '256, 68, 0)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResStringPool_header()
        expected = 28
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0, 0x100, 0x44,
            0)
        expected = b'\1\0\x1c\0\x94\0\0\0' + \
        b'\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0\0\0\0\0'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\1\0\x1c\0\x94\0\0\0' + \
        b'\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0\0\0\0\0' + \
        b'\x13\x37'
        expected = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0, 0x100, 0x44,
            0), b'\x13\x37'
        actual = ResStringPool_header.from_bytes(invector)

        self.assertEqual(expected, actual)

    def test_Flag_bytes(self):
        invector = ResStringPool_header.Flags.UTF8_FLAG
        expected = b'\0\1\0\0'
        actual = bytes(reversed(bytes(invector)))

        self.assertEqual(expected, actual)

    def test_Flag_from_bytes(self):
        invector = b'\0\1\0\0\x13\x37'
        expected = ResStringPool_header.Flags.UTF8_FLAG, b'\x13\x37'
        actual = ResStringPool_header.Flags.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)
