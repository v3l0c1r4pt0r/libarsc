#!/usr/bin/env python3
## \file types.py
# \brief resource types in ARSC file
import unittest
from arsc.type.enum import Enum

class ResourceType(Enum):
    RES_NULL_TYPE = 0x0000
    ## ResChunk_header is part of \link stringpool.ResStringPool \endlink
    RES_STRING_POOL_TYPE = 0x0001
    ## ResChunk_header is part of \link table.ResTable_header \endlink
    RES_TABLE_TYPE = 0x0002
    RES_XML_TYPE = 0x0003
    # Chunk types in RES_XML_TYPE
    RES_XML_FIRST_CHUNK_TYPE = 0x0100
    RES_XML_START_NAMESPACE_TYPE = 0x0100
    RES_XML_END_NAMESPACE_TYPE = 0x0101
    RES_XML_START_ELEMENT_TYPE = 0x0102
    RES_XML_END_ELEMENT_TYPE = 0x0103
    RES_XML_CDATA_TYPE = 0x0104
    RES_XML_LAST_CHUNK_TYPE = 0x017f
    # This contains a uint32_t array mapping strings in the string
    # pool back to resource identifiers.  It is optional.
    RES_XML_RESOURCE_MAP_TYPE = 0x0180
    # Chunk types in RES_TABLE_TYPE
    ## ResChunk_header is part of \link table.ResTable_package \endlink
    RES_TABLE_PACKAGE_TYPE = 0x0200
    RES_TABLE_TYPE_TYPE = 0x0201
    RES_TABLE_TYPE_SPEC_TYPE = 0x0202


class ResourceTypeTests(unittest.TestCase):

    def test_init(self):
        invector = 0x17f
        expected = ResourceType.RES_XML_LAST_CHUNK_TYPE
        actual = ResourceType(invector)

        self.assertEqual(expected, actual)

    def test_index(self):
        invector = 'RES_XML_LAST_CHUNK_TYPE'
        expected = ResourceType.RES_XML_LAST_CHUNK_TYPE
        actual = ResourceType[invector]

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResourceType.RES_XML_LAST_CHUNK_TYPE
        expected = b'\x7f\x01'
        actual = bytes(invector)
        # enums does not support endianness specification, so reverse
        actual = bytes(reversed(actual))

        self.assertEqual(expected, actual)

    def test_frombytes(self):
        invector = b'\x7f\x01\xa5\x5a'
        expected = ResourceType.RES_XML_LAST_CHUNK_TYPE, b'\xa5\x5a'
        actual = ResourceType.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = ResourceType.RES_XML_LAST_CHUNK_TYPE
        expected = 'ResourceType.RES_XML_LAST_CHUNK_TYPE'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResourceType.RES_TABLE_TYPE
        expected = 2
        actual = len(invector)

        self.assertEqual(expected, actual)
