#!/usr/bin/env python3
## \file type.py
# \brief ResTable_typeSpec and ResTable_type
import unittest
from arsc.type.uint8 import uint8
from arsc.type.uint16 import uint16
from arsc.type.uint32 import uint32
from arsc.chunk import ResChunk_header
from arsc.types import ResourceType
from arsc.config import ResTable_config
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResTable_typeSpec_header
#  \brief A specification of the resources defined by a particular type.
#  \details There should be one of these chunks for each resource type.
#
#  This structure is followed by an array of integers providing the set of
#  configuration change flags (ResTable_config::CONFIG_*) that have multiple
#  resources for that configuration.  In addition, the high bit is set if that
#  resource has been made public.
class ResTable_typeSpec_header:

    len = 16

    def __init__(self, header=None, id=1, res0=0, res1=0, entryCount=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_TABLE_TYPE_SPEC_TYPE,
                    headerSize=ResTable_typeSpec_header.len,
                    size=ResTable_typeSpec_header.len)
        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_TABLE_TYPE_SPEC_TYPE:
            raise ChunkHeaderWrongTypeException(
                    ResourceType.RES_TABLE_TYPE_SPEC_TYPE)

        if not isinstance(id, uint8):
            id = uint8(id, little=True)

        if not isinstance(res0, uint8):
            res0 = uint8(res0, little=True)

        if not isinstance(res1, uint16):
            res1 = uint16(res1, little=True)

        if not isinstance(entryCount, uint32):
            entryCount = uint32(entryCount, little=True)

        self.header = header
        ## The type identifier this chunk is holding.  Type IDs start
        #  at 1 (corresponding to the value of the type bits in a
        #  resource identifier).  0 is invalid.
        self.id = id
        ## Must be 0.
        self.res0 = res0
        ## Must be 0.
        self.res1 = res1
        ## Number of uint32_t entry configuration masks that follow.
        self.entryCount = entryCount

    def __str__(self):
        return '{{header={header}, id={id}, res0={res0}, res1={res1}, '\
                'entryCount={entryCount}}}'.format(header=str(self.header),
                        id=str(self.id), res0=str(self.res0),
                        res1=str(self.res1), entryCount=str(self.entryCount))

    def __repr__(self):
        return '{c}({header}, {id}, {res0}, {res1}, {entryCount})'.format(
                c=type(self).__name__, header=repr(self.header), id=self.id,
                res0=self.res0, res1=self.res1, entryCount=self.entryCount)

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.id == rhs.id and \
                self.res0 == rhs.res0 and \
                self.res1 == rhs.res1 and \
                self.entryCount == rhs.entryCount

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        id = bytes(self.id)
        res0 = bytes(self.res0)
        res1 = bytes(self.res1)
        entryCount = bytes(self.entryCount)

        return header + id + res0 + res1 + entryCount

    def from_bytes(b, little=True):
        header, b = ResChunk_header.from_bytes(b)
        id, b = uint8.from_bytes(b)
        res0, b = uint8.from_bytes(b)
        res1, b = uint16.from_bytes(b, True)
        entryCount, b = uint32.from_bytes(b, True)

        return ResTable_typeSpec_header(header, id, res0, res1, entryCount), b


## \class ResTable_typeSpec
class ResTable_typeSpec:

    def __init__(self, header=None, configs=None):
        if header is None:
            header = ResTable_typeSpec_header()

        if configs is None:
            configs = []

        if not isinstance(header, ResTable_typeSpec_header):
            raise WrongTypeException('header', ResTable_typeSpec_header)

        ## Instance of ResTable_typeSpec_header
        self.header = header
        self.configs = configs

    def __str__(self):
        return '{{header={header}, configs={configs}}}'.format(
                header=str(self.header), configs=str(self.configs))

    def __repr__(self):
        return '{c}({header}, {configs})'.format(c=type(self).__name__,
                header=repr(self.header), configs=repr(self.configs))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.configs == rhs.configs

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        configs = bytes(self.configs)

        return header + configs

    def from_bytes(b, little=True):
        header, b = ResTable_typeSpec_header.from_bytes(b)
        # FIXME: implement object contents
        restlen = header.header.size.integer - header.header.headerSize.integer
        rest, b = b[:restlen], b[restlen:]

        return ResTable_typeSpec(header, rest), b


## \class ResTable_type_header
#  \brief A collection of resource entries for a particular resource data type.
#  \details Followed by an array of uint32_t defining the resource
#  values, corresponding to the array of type strings in the
#  ResTable_package::typeStrings string block. Each of these hold an
#  index from entriesStart; a value of NO_ENTRY means that entry is
#  not defined.
#  
#  There may be multiple of these chunks for a particular resource type,
#  supply different configuration variations for the resource values of
#  that type.
#  
#  It would be nice to have an additional ordered index of entries, so
#  we can do a binary search if trying to find a resource by string name.
class ResTable_type_header:

    len = 0x44

    def __init__(self, header=None, id=1, res0=0, res1=0, entryCount=0,
            entriesStart=0, config=None):
        if header is None:
            header = ResChunk_header(ResourceType.RES_TABLE_TYPE_TYPE,
                    headerSize=ResTable_type_header.len,
                    size=ResTable_type_header.len)

        if config is None:
            config = ResTable_config()

        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_TABLE_TYPE_TYPE:
            raise ChunkHeaderWrongTypeException(
                    ResourceType.RES_TABLE_TYPE_TYPE)

        if not isinstance(id, uint8):
            id = uint8(id, little=True)

        if not isinstance(res0, uint8):
            res0 = uint8(res0, little=True)

        if not isinstance(res1, uint16):
            res1 = uint16(res1, little=True)

        if not isinstance(entryCount, uint32):
            entryCount = uint32(entryCount, little=True)

        if not isinstance(entriesStart, uint32):
            entriesStart = uint32(entriesStart, little=True)

        if not isinstance(config, ResTable_config):
            config = ResTable_config(config)

        self.header = header
        ## The type identifier this chunk is holding.  Type IDs start
        #  at 1 (corresponding to the value of the type bits in a
        #  resource identifier).  0 is invalid.
        self.id = id
        ## Must be 0.
        self.res0 = res0
        ## Must be 0.
        self.res1 = res1
        ## Number of uint32_t entry configuration masks that follow.
        self.entryCount = entryCount
        self.entriesStart = entriesStart
        self.config = config

    def __str__(self):
        return '{{header={header}, id={id}, res0={res0}, res1={res1}, '\
                'entryCount={entryCount}, entriesStart={entriesStart}, ' \
                'config={config}}}'.format(header=str(self.header),
                        id=str(self.id), res0=str(self.res0),
                        res1=str(self.res1), entryCount=str(self.entryCount),
                        entriesStart=str(self.entriesStart),
                        config=repr(bytes(self.config)))

    def __repr__(self):
        return '{c}({header}, {id}, {res0}, {res1}, {entryCount}, ' \
                '{entriesStart}, {config})'.format(
                c=type(self).__name__, header=repr(self.header), id=self.id,
                res0=self.res0, res1=self.res1, entryCount=self.entryCount,
                entriesStart=self.entriesStart, config=repr(bytes(self.config)))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.id == rhs.id and \
                self.res0 == rhs.res0 and \
                self.res1 == rhs.res1 and \
                self.entryCount == rhs.entryCount and \
                self.entriesStart == rhs.entriesStart and \
                self.config == rhs.config

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        id = bytes(self.id)
        res0 = bytes(self.res0)
        res1 = bytes(self.res1)
        entryCount = bytes(self.entryCount)
        entriesStart = bytes(self.entriesStart)
        config = bytes(self.config)

        return header + id + res0 + res1 + entryCount + entriesStart + config

    def from_bytes(b, little=True):
        header, b = ResChunk_header.from_bytes(b)
        id, b = uint8.from_bytes(b)
        res0, b = uint8.from_bytes(b)
        res1, b = uint16.from_bytes(b, True)
        entryCount, b = uint32.from_bytes(b, True)
        entriesStart, b = uint32.from_bytes(b, True)
        config, b = ResTable_config.from_bytes(b)

        return ResTable_type_header(header, id, res0, res1, entryCount,
                entriesStart, config), b


## \class ResTable_type
class ResTable_type:

    def __init__(self, header=None, rest=None):
        if header is None:
            header = ResTable_type_header()

        if rest is None:
            rest = []

        if not isinstance(header, ResTable_type_header):
            raise WrongTypeException('header', ResTable_type_header)

        ## Instance of ResTable_type_header
        self.header = header
        self.rest = rest

    def __str__(self):
        return '{{header={header}, rest={rest}}}'.format(
                header=str(self.header), rest=str(self.rest))

    def __repr__(self):
        return '{c}({header}, {rest})'.format(c=type(self).__name__,
                header=repr(self.header), rest=repr(self.rest))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.rest == rhs.rest

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        rest = bytes(self.rest)

        return header + rest

    def from_bytes(b, little=True):
        header, b = ResTable_type_header.from_bytes(b)
        # FIXME: implement object contents
        restlen = header.header.size.integer - header.header.headerSize.integer
        rest, b = b[:restlen], b[restlen:]

        return ResTable_type(header, rest), b


class ResTable_typeSpec_headerTests(unittest.TestCase):

    tv1_bytes = b'\2\2\x10\0\x20\0\0\0' + b'\2\0\0\0\4\0\0\0'

    tv1_obj = \
            ResTable_typeSpec_header(
                ResChunk_header(
                    ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32
                ),
                2, 0, 0, 4
            )

    def test_str(self):
        invector = ResTable_typeSpec_headerTests.tv1_obj
        expected = '{header={type=ResourceType.RES_TABLE_TYPE_SPEC_TYPE, ' \
                'headerSize=16, size=32}, id=2, res0=0, res1=0, entryCount=4}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_typeSpec_headerTests.tv1_obj
        expected = 'ResTable_typeSpec_header(ResChunk_header(' \
                'ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32), 2, 0, 0, 4)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTable_typeSpec_headerTests.tv1_obj
        expected = 16
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_typeSpec_headerTests.tv1_obj
        expected = ResTable_typeSpec_headerTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTable_typeSpec_headerTests.tv1_bytes + b'\x13\x37'
        expected = ResTable_typeSpec_headerTests.tv1_obj, b'\x13\x37'
        actual = ResTable_typeSpec_header.from_bytes(invector)

        self.assertEqual(expected, actual)


class ResTable_typeSpecTests(unittest.TestCase):

    tv1_bytes = b'\2\2\x10\0\x20\0\0\0' + b'\2\0\0\0\4\0\0\0' + (b'\0\5\0\0' * 4)

    tv1_obj = \
            ResTable_typeSpec(
                ResTable_typeSpec_header(
                    ResChunk_header(
                        ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32
                    ),
                    2, 0, 0, 4
                ),
                (b'\0\5\0\0' * 4)
            )

    def test_str(self):
        invector = ResTable_typeSpecTests.tv1_obj
        expected = '{header={header={type=ResourceType.RES_TABLE_TYPE_SPEC_TYPE, ' \
                'headerSize=16, size=32}, id=2, res0=0, res1=0, entryCount=4}, '\
                'configs=' + repr(b'\0\5\0\0' * 4) + '}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_typeSpecTests.tv1_obj
        expected = 'ResTable_typeSpec(ResTable_typeSpec_header(ResChunk_header(' \
                'ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32), 2, 0, 0, ' \
                '4), ' + repr(b'\0\5\0\0' * 4) + ')'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTable_typeSpecTests.tv1_obj
        expected = 32
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_typeSpecTests.tv1_obj
        expected = ResTable_typeSpecTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTable_typeSpecTests.tv1_bytes + b'\x13\x37'
        expected = ResTable_typeSpecTests.tv1_obj, b'\x13\x37'
        actual = ResTable_typeSpec.from_bytes(invector)

        self.assertEqual(expected, actual)


class ResTable_type_headerTests(unittest.TestCase):

    tv1_bytes = b'\1\2\x44\0\x74\0\0\0' + b'\2\0\0\0\4\0\0\0\x54\0\0\0' + \
            b'\x30' + bytes(0x2f)

    tv1_obj = \
            ResTable_type_header(
                ResChunk_header(
                    ResourceType.RES_TABLE_TYPE_TYPE, 68, 116
                ),
                2, 0, 0, 4, 0x54,
                ResTable_config(0x30)
            )

    def test_str(self):
        invector = ResTable_type_headerTests.tv1_obj
        expected = '{header={type=ResourceType.RES_TABLE_TYPE_TYPE, ' \
                'headerSize=68, size=116}, id=2, res0=0, res1=0, entryCount=4, '\
                'entriesStart=84, config='+repr(b'\x30' + bytes(0x2f))+'}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_type_headerTests.tv1_obj
        expected = 'ResTable_type_header(ResChunk_header(' \
                'ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 2, 0, 0, 4, '\
                '84, '+repr(b'\x30' + bytes(0x2f))+')'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTable_type_headerTests.tv1_obj
        expected = 0x44
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_type_headerTests.tv1_obj
        expected = ResTable_type_headerTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTable_type_headerTests.tv1_bytes + b'\x13\x37'
        expected = ResTable_type_headerTests.tv1_obj, b'\x13\x37'
        actual = ResTable_type_header.from_bytes(invector)

        self.assertEqual(expected, actual)


class ResTable_typeTests(unittest.TestCase):

    tv1_bytes = b'\1\2\x44\0\x74\0\0\0' + b'\2\0\0\0\4\0\0\0\x54\0\0\0' + \
            b'\x30' + bytes(0x2f) + \
            b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
            ((b'\x08' + bytes(7)) * 4)

    tv1_obj = \
            ResTable_type(
                ResTable_type_header(
                    ResChunk_header(
                        ResourceType.RES_TABLE_TYPE_TYPE, 68, 116
                    ),
                    2, 0, 0, 4, 84,
                    ResTable_config(0x30)
                ),
                b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
                ((b'\x08' + bytes(7)) * 4)
            )

    def test_str(self):
        invector = ResTable_typeTests.tv1_obj
        expected = '{header={header={type=ResourceType.RES_TABLE_TYPE_TYPE, ' \
                'headerSize=68, size=116}, id=2, res0=0, res1=0, ' \
                'entryCount=4, entriesStart=84, config=' + \
                repr(b'0'+bytes(0x2f))+'}, '\
                'rest=' + repr(b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
                ((b'\x08' + bytes(7)) * 4)) + '}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_typeTests.tv1_obj
        expected = 'ResTable_type(ResTable_type_header(ResChunk_header(' \
                'ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 2, 0, 0, ' \
                '4, 84, '+repr(b'0'+bytes(0x2f))+'), ' + \
                repr(b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
                ((b'\x08' + bytes(7)) * 4)) + ')'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTable_typeTests.tv1_obj
        expected = 116
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_typeTests.tv1_obj
        expected = ResTable_typeTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTable_typeTests.tv1_bytes + b'\x13\x37'
        expected = ResTable_typeTests.tv1_obj, b'\x13\x37'
        actual = ResTable_type.from_bytes(invector)

        self.assertEqual(expected, actual)
