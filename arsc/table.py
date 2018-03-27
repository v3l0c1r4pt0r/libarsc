#!/usr/bin/env python3
## \file table.py
# \brief ResTable and related
import unittest
from arsc.type.uint32 import uint32
from arsc.type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.types import ResourceType
from arsc.external.configuration import AConfiguration
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResTable_header
# \brief Header for a resource table
# \details Its data contains a series of
# additional chunks:
#   * A ResStringPool_header containing all table values.  This string pool
#     contains all of the string values in the entire resource table (not
#     the names of entries or type identifiers however).
#   * One or more ResTable_package chunks.
#
# Specific entries within a resource table can be uniquely identified
# with a single integer as defined by the ResTable_ref structure.
class ResTable_header:

    len = 0xc

    def __init__(self, header=None, packageCount=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_TABLE_TYPE,
                    headerSize=ResTable_header.len, size=ResTable_header.len)
        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_TABLE_TYPE:
            raise ChunkHeaderWrongTypeException(ResourceType.RES_TABLE_TYPE,
                    header.type)
        self.header = header

        if isinstance(packageCount, uint32):
            self.packageCount = packageCount
        else:
            self.packageCount = uint32(packageCount, little=True)

    def __str__(self):
        return '{{header={header}, '\
                'packageCount={packageCount}}}'.format(header=str(self.header),
                        packageCount=str(self.packageCount))

    def __repr__(self):
        return '{c}({header}, {packageCount})'.format(c=type(self).__name__,
                header=repr(self.header), packageCount=self.packageCount)

    def __eq__(self, rhs):
        return type(self) == type(rhs) and self.header == rhs.header and \
                self.packageCount == rhs.packageCount

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        packageCount = bytes(self.packageCount)

        return header + packageCount

    def from_bytes(b, little=True):
        header, b = ResChunk_header.from_bytes(b)
        packageCount, b = uint32.from_bytes(b, little=True)

        return ResTable_header(header, packageCount), b


class ResTable_headerTests(unittest.TestCase):

    def test_header_is_expected(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE))
        expected = ResChunk_header
        actual = type(invector.header)

        self.assertEqual(expected, actual)

    def test_header_is_unexpected(self):
        with self.assertRaises(Exception) as cm: # FIXME: SerializationError would be better
            invector = ResTable_header(b'\x02\x00\x0c\x00\xac\xa3\x01\x00')

        expected = 'header must be of type ResChunk_header'
        _, actual = cm.exception.args

        self.assertEqual(expected, actual)

    def test_header_describes_wrong_type(self):
        with self.assertRaises(Exception) as cm:
            invector = ResTable_header(ResChunk_header())

        expected = 'header must describe resource of type '\
                'ResourceType.RES_TABLE_TYPE'
        _, actual = cm.exception.args

        self.assertEqual(expected, actual)

    def test_packageCount_is_uint32(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE),
                uint32(0x8331337))
        expected = uint32
        actual = type(invector.packageCount)

        self.assertEqual(expected, actual)

    def test_packageCount_is_uintable(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE),
                0x8331337)
        expected = uint32
        actual = type(invector.packageCount)

        self.assertEqual(expected, actual)

    @unittest.skip('Not working because of uint32 error')
    def test_packageCount_is_not_uintable(self):
        with self.assertRaises(TypeError) as cm:
            invector = ResTable_header(ResChunk_header(
                ResourceType.RES_TABLE_TYPE), 'be elite')

        expected = 'Error'
        actual = cm.exception.message

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE,
            0xc, 0x1a3ac), 1)
        expected = '{header={type=ResourceType.RES_TABLE_TYPE, headerSize=12, '\
        'size=107436}, packageCount=1}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE,
            0xc, 0x1a3ac), 1)
        expected = 'ResTable_header(ResChunk_header('\
                'ResourceType.RES_TABLE_TYPE, 12, 107436), 1)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_diff_type_is_neq(self):
        lhs = ResTable_header()
        rhs = b'\x13\x37'

        self.assertNotEqual(lhs, rhs)

    def test_len(self):
        invector = ResTable_header()
        expected = 0xc
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE,
            0xc, 0x1a3ac), 1)
        expected = b'\x02\x00\x0c\x00\xac\xa3\x01\x00\x01\x00\x00\x00'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\x02\x00\x0c\x00\xac\xa3\x01\x00\x01\x00\x00\x00\x13\x37'
        expected = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE,
            0xc, 0x1a3ac), 1), b'\x13\x37'
        actual = ResTable_header.from_bytes(invector)

        self.assertEqual(expected, actual)

    def test_objects_are_not_same(self):
        invector1 = ResTable_header()
        invector2 = ResTable_header()
        invector1.header.size = uint32(123)

        self.assertIsNot(invector1, invector2)
        self.assertNotEqual(invector1, invector2)
