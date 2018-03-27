#!/usr/bin/env python3
## \file stringpool.py
# \brief ResStringPool and related
import unittest
from arsc.type.uint32 import uint32
from arsc.type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.table import ResTable_header
from arsc.types import ResourceType
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResStringPool_header
#
#  \brief Definition for a pool of strings.
#  \details The data of this chunk is an
#  array of uint32_t providing indices into the pool, relative to
#  stringsStart.  At stringsStart are all of the UTF-16 strings
#  concatenated together; each starts with a uint16_t of the string's
#  length and each ends with a 0x0000 terminator.  If a string is >
#  32767 characters, the high bit of the length is set meaning to take
#  those 15 bits as a high word and it will be followed by another
#  uint16_t containing the low word.
#
#  If styleCount is not zero, then immediately following the array of
#  uint32_t indices into the string table is another array of indices
#  into a style table starting at stylesStart.  Each entry in the
#  style table is an array of ResStringPool_span structures.
class ResStringPool_header:

    len = 28

    def __init__(self, header=None, stringCount=0, styleCount=0, flags=0,
            stringsStart=0, stylesStart=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_STRING_POOL_TYPE,
                    headerSize=ResStringPool_header.len,
                    size=ResStringPool_header.len)
        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_STRING_POOL_TYPE:
            raise ChunkHeaderWrongTypeException(
                    ResourceType.RES_STRING_POOL_TYPE)
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

        if isinstance(flags, ResStringPool_header.Flags):
            ## Flags.
            self.flags = flags
        else:
            self.flags = ResStringPool_header.Flags(flags)

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
                styleCount=self.styleCount, flags=str(self.flags),
                stringsStart=self.stringsStart, stylesStart=self.stylesStart)

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.stringCount == rhs.stringCount and \
                self.styleCount == rhs.styleCount and \
                self.flags == rhs.flags and \
                self.stringsStart == rhs.stringsStart and \
                self.stylesStart == rhs. stylesStart

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        stringCount = bytes(self.stringCount)
        styleCount = bytes(self.styleCount)
        flags = bytes(reversed(bytes(self.flags)))
        stringsStart = bytes(self.stringsStart)
        stylesStart = bytes(self.stylesStart)

        return header + stringCount + styleCount + flags + stringsStart + \
                stylesStart

    def from_bytes(b, little=True):
        header, b = ResChunk_header.from_bytes(b)
        stringCount, b = uint32.from_bytes(b, little=True)
        styleCount, b = uint32.from_bytes(b, little=True)
        flags, b = ResStringPool_header.Flags.from_bytes(b, little=True)
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


## \class ResStringPool
class ResStringPool:

    ## Converts every element of list to newtype
    def _convert_list_elements(l, newtype):
        for i, e in enumerate(l):
            l[i] = newtype(e)

    ## Splits COUNT number of elements of fixed-length ELEM_TYPE from BUF
    def _split_fixed_list(buf, count, elem_type):
        b = buf
        ret = []
        for i in range(count):
            e, b = elem_type.from_bytes(b, little=True)
            ret.append(e)
        return ret, b

    ## Splits BUF into list of buffers, whose lengths are in LENGTH_LIST
    def _split_variable_length_strings(buf, length_list):
        ret = []
        b = buf
        for l in length_list:
            e, b = b[:l], b[l:]
            ret.append(e)
        return ret

    ## Counts lengths between offsets and returns them as list
    def _offsets_to_length(o):
        return [o[i+1].integer-a.integer for i,a in enumerate(o[:-1])]

    def __init__(self, header=None, strrefs=None, stylerefs=None, strings=None,
            styles=None):
        if header is None:
            header = ResStringPool_header(ResChunk_header(
                    ResourceType.RES_STRING_POOL_TYPE,
                    headerSize=ResStringPool_header.len,
                    size=ResStringPool_header.len),
                    stringCount=0, styleCount=0, flags=0, stringsStart=0,
                    stylesStart=0)
        if not isinstance(header, ResStringPool_header):
            raise WrongTypeException(ResStringPool_header)
        ## StringPool description as ResStringPool_header object
        self.header = header

        # set default values
        if strrefs is None:
            strrefs = []

        if stylerefs is None:
            stylerefs = []

        if strings is None:
            strings = []

        if styles is None:
            styles = []

        # check types
        if not isinstance(strrefs, list):
            raise WrongTypeException('strrefs', list)

        if not isinstance(stylerefs, list):
            raise WrongTypeException('stylerefs', list)

        if not isinstance(strings, list):
            raise WrongTypeException('strings', list)

        if not isinstance(styles, list):
            raise WrongTypeException('styles', list)

        # convert list elements, if not uints
        if isinstance(strrefs, list) and len(strrefs) > 0 and \
                not isinstance(strrefs[0], uint32):
            ResStringPool._convert_list_elements(strrefs, uint32)
        # TODO: create interface in uint* for changing endianness
        for e in strrefs:
            e.little = True
            e._endian = '<'

        if isinstance(stylerefs, list) and len(stylerefs) > 0 and \
                not isinstance(stylerefs[0], uint32):
            ResStringPool._convert_list_elements(stylerefs, uint32)
        for e in strrefs:
            e.little = True
            e._endian = '<'

        ## References to strings.
        #  List of \link type.uint32.uint32 \endlink. Offset into self.strings.
        self.strrefs = strrefs
        ## References to styles.
        #  List of \link type.uint32.uint32 \endlink. Offset into self.styles.
        self.stylerefs = stylerefs
        ## String pool
        # Consists of strings, ending with NULLs and preceded by their lengths
        # (twice). Strings might be UTF-16 or UTF-8, depending on header flags.
        self.strings = strings
        ## Style span pool
        # Each entry in the style table is an array of ResStringPool_span
        # structures.
        self.styles = styles

    def __str__(self):
        return '{{header={header}, strrefs={strrefs}, stylerefs={stylerefs}, ' \
                'strings={strings}, styles={styles}}}'.format(
                        header=str(self.header), strrefs=repr(self.strrefs),
                        stylerefs=repr(self.stylerefs),
                        strings=repr(self.strings), styles=repr(self.styles))

    def __repr__(self):
        return '{c}({header}, {strrefs}, {stylerefs}, {strings}, {styles})'. \
                format(c=type(self).__name__, header=repr(self.header),
                        strrefs=repr(self.strrefs),
                        stylerefs=repr(self.stylerefs),
                        strings=repr(self.strings), styles=repr(self.styles))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.strrefs == rhs.strrefs and \
                self.strings == rhs.strings and \
                self.stylerefs == rhs.stylerefs and \
                self.styles == rhs.styles

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)

        # FIXME: determine position and order of strings and styles using header
        strrefs = bytes()
        for ref in self.strrefs:
            strrefs += bytes(ref)

        stylerefs = bytes()
        for ref in self.stylerefs:
            stylerefs += bytes(ref)

        strings = bytes()
        for s in self.strings:
            strings += bytes(s)
        styles = bytes()
        for s in self.styles:
            styles += bytes(s)

        return header + strrefs + stylerefs + strings + styles

    def from_bytes(b, little=True):
        content = b
        header, b = ResStringPool_header.from_bytes(b)

        # drop everything inside size declared in ResStringPool_header
        content, rest = content[:header.header.size.integer], \
        content[header.header.size.integer:]

        # split content
        strrefslen = header.stringCount.integer * len(uint32(0))
        stylerefslen = header.styleCount.integer * len(uint32(0))

        if strrefslen > 0:
            strrefs_b, b = b[:strrefslen], b[strrefslen:]
            strings_b = content[header.stringsStart.integer:]
        else:
            strrefs_b = bytes()
            strings_b = bytes()

        if stylerefslen > 0:
            stylerefs_b, b = b[:stylerefslen], b[stylerefslen:]
            styles_b = content[header.stylesStart.integer:]
        else:
            stylerefs_b = bytes()
            styles_b = bytes()

        # split ref list buffers into Python lists
        strrefs, r = ResStringPool._split_fixed_list(strrefs_b,
                header.stringCount.integer, uint32)
        if len(r) > 0:
            raise Exception('String pool inconsistent')
        stylerefs, r = ResStringPool._split_fixed_list(stylerefs_b,
                header.styleCount.integer, uint32)
        if len(r) > 0:
            raise Exception('Style span pool inconsistent')

        # count lengths of entries
        strlengths = ResStringPool._offsets_to_length(strrefs + \
                [uint32(len(strings_b))])
        stylelengths = ResStringPool._offsets_to_length(stylerefs + \
                [uint32(len(styles_b))])

        # split strings and styles into lists
        strings = ResStringPool._split_variable_length_strings(strings_b, strlengths)
        styles = ResStringPool._split_variable_length_strings(styles_b,
                stylelengths)

        return ResStringPool(header, strrefs, stylerefs, strings,
                styles), rest


class ResStringPool_headerTests(unittest.TestCase):

    def test_str(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0,
            ResStringPool_header.Flags.UTF8_FLAG, 0x44, 0)
        expected = '{header={type=ResourceType.RES_STRING_POOL_TYPE, ' \
                'headerSize=28, size=148}, stringCount=10, styleCount=0, ' \
                'flags=Flags.UTF8_FLAG, ' \
                'stringsStart=68, stylesStart=0}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0,
            ResStringPool_header.Flags.UTF8_FLAG, 0x44, 0)
        expected = 'ResStringPool_header(ResChunk_header(' \
                'ResourceType.RES_STRING_POOL_TYPE, 28, 148), 10, 0, ' \
                'Flags.UTF8_FLAG, 68, 0)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResStringPool_header()
        expected = 28
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0,
            ResStringPool_header.Flags.UTF8_FLAG, 0x44, 0)
        expected = b'\1\0\x1c\0\x94\0\0\0' + \
        b'\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0\0\0\0\0'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\1\0\x1c\0\x94\0\0\0' + \
        b'\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0\0\0\0\0' + \
        b'\x13\x37'
        expected = ResStringPool_header(ResChunk_header(
            ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0,
            ResStringPool_header.Flags.UTF8_FLAG, 0x44, 0), b'\x13\x37'
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


class ResStringPoolTests(unittest.TestCase):

    tv1_bytes = \
            b'\1\0\x1c\0\x94\0\0\0\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0' + \
            b'\0\0\0\0\0\0\0\0\7\0\0\0\x12\0\0\0\x1b\0\0\0\x21\0\0\0' + \
            b'\x29\0\0\0\x31\0\0\0\x3a\0\0\0\x42\0\0\0\x49\0\0\0\4\4attr\0' + \
            b'\x08\x08drawable\0\6\6layout\0\3\3raw\0\5\5color\0\5\5dimen\0' + \
            b'\6\6string\0\5\5style\0\4\4menu\0\2\2id\0' + \
            b'\0\0' # FIXME: padding ??

    tv1_obj = ResStringPool(ResStringPool_header(ResChunk_header(
        ResourceType.RES_STRING_POOL_TYPE, 0x1c, 0x94), 10, 0,
        ResStringPool_header.Flags.UTF8_FLAG, 0x44, 0), strrefs=[0x0, 0x7, 0x12,
            0x1b, 0x21, 0x29, 0x31, 0x3a, 0x42, 0x49], strings=[b'\4\4attr\0',
                b'\x08\x08drawable\0', b'\6\6layout\0', b'\3\3raw\0',
                b'\5\5color\0', b'\5\5dimen\0', b'\6\6string\0', b'\5\5style\0',
                b'\4\4menu\0', b'\2\2id\0' + b'\0\0'])

    def test_str(self):
        invector = ResStringPoolTests.tv1_obj
        expected = '{header={header={type=ResourceType.RES_STRING_POOL_TYPE, ' \
                'headerSize=28, size=148}, stringCount=10, styleCount=0, ' \
                'flags=Flags.UTF8_FLAG, ' \
                'stringsStart=68, stylesStart=0}, strrefs=[uint32(0), ' \
                'uint32(7), uint32(18), uint32(27), uint32(33), uint32(41), ' \
                'uint32(49), uint32(58), uint32(66), uint32(73)], ' \
                "stylerefs=[], strings=[b'\\x04\\x04attr\\x00', " \
                "b'\\x08\\x08drawable\\x00', b'\\x06\\x06layout\\x00', " \
                "b'\\x03\\x03raw\\x00', b'\\x05\\x05color\\x00', " \
                "b'\\x05\\x05dimen\\x00', b'\\x06\\x06string\\x00', " \
                "b'\\x05\\x05style\\x00', b'\\x04\\x04menu\\x00', " \
                "b'\\x02\\x02id\\x00\\x00\\x00'], styles=[]}"
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResStringPoolTests.tv1_obj
        expected = 'ResStringPool(ResStringPool_header(ResChunk_header(' \
                'ResourceType.RES_STRING_POOL_TYPE, 28, 148), 10, 0, ' \
                'Flags.UTF8_FLAG, 68, 0), [uint32(0), uint32(7), uint32(18), ' \
                'uint32(27), uint32(33), uint32(41), uint32(49), uint32(58), ' \
                'uint32(66), uint32(73)], [], ' \
                "[b'\\x04\\x04attr\\x00', b'\\x08\\x08drawable\\x00', " \
                "b'\\x06\\x06layout\\x00', b'\\x03\\x03raw\\x00', " \
                "b'\\x05\\x05color\\x00', b'\\x05\\x05dimen\\x00', " \
                "b'\\x06\\x06string\\x00', b'\\x05\\x05style\\x00', " \
                "b'\\x04\\x04menu\\x00', b'\\x02\\x02id\\x00\\x00\\x00'], " \
                '[])'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResStringPool_header()
        expected = 28
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResStringPoolTests.tv1_obj
        expected = ResStringPoolTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    @unittest.skip('Padding not working')
    def test_from_bytes(self):
        invector = ResStringPoolTests.tv1_bytes + b'\x13\x37'
        expected = ResStringPoolTests.tv1_obj, b'\x13\x37'
        actual = ResStringPool.from_bytes(invector)

        self.assertEqual(expected, actual)
