#!/usr/bin/env python3
## \file arsc.py
# \brief Main resource table functionality
import unittest
from arsc.type.uint32 import uint32
from arsc.chunk import ResChunk_header
from arsc.table import ResTable_header
from arsc.types import ResourceType
from arsc.package import ResTable_package
from arsc.package import ResTable_package_header
from arsc.stringpool import ResStringPool
from arsc.stringpool import ResStringPool_header
from arsc.tabletype import ResTable_typeSpec
from arsc.tabletype import ResTable_typeSpec_header
from arsc.tabletype import ResTable_type
from arsc.tabletype import ResTable_type_header
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResTable
class ResTable:

    def __init__(self, header=None, values=None, packages=None):
        # handle defaults
        if header is None:
            header = ResTable_header()

        if values is None:
            values = ResStringPool()

        if packages is None:
            packages = []

        # check input types
        if not isinstance(header, ResTable_header):
            raise WrongTypeException('header', ResTable_header)

        if not isinstance(values, ResStringPool):
            raise WrongTypeException('values', ResStringPool)

        if not isinstance(packages, list):
            raise WrongTypeException('packages', list)

        if len(packages) > 0 and not isinstance(packages[0], ResTable_package):
            raise WrongTypeException('packages[0]', ResTable_package)

        # store in object
        ## table.ResTable_header instance. Defines length of resource table and
        #  number of packages.
        self.header = header
        ## stringpool.ResStringPool storing values of resources (not their
        #  names!).
        self.values = values
        ## List of package.ResTable_package of length defined in
        #  table.ResTable_header. Stores all resource names and attributes.
        self.packages = packages

    def __str__(self):
        pkgstrlist = []
        for pkg in self.packages:
            pkgstrlist.append(str(pkg))
        packages = '[{}]'.format(', '.join(pkgstrlist))
        return '{{header={header}, values={values}, packages={packages}}}'.\
                format(header=str(self.header), values=str(self.values),
                        packages=packages)

    def __repr__(self):
        return '{c}({header}, {values}, {packages})'.format(c=type(self).__name__,
                header=repr(self.header), values=repr(self.values),
                packages=repr(self.packages))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.values == rhs.values and \
                self.packages == rhs.packages

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        values = bytes(self.values)
        packages = bytes()
        for pkg in self.packages:
            packages += bytes(pkg)

        return header + values + packages

    def from_bytes(b, little=True):
        header, b = ResTable_header.from_bytes(b)
        values, b = ResStringPool.from_bytes(b)
        packages = []
        for i in range(header.packageCount.integer):
            pkg, b = ResTable_package.from_bytes(b)
            packages.append(pkg)

        return ResTable(header, values, packages), b


class ResTableTests(unittest.TestCase):

    Flags = ResStringPool_header.Flags

    # ResTable_header
    table_header = b'\x02\x00\x0c\x00\x32\3\0\0\x01\x00\x00\x00'

    # ResStringPool
    value_strings = \
            b'\1\0\x1c\0\x1c\0\0\0' + \
            b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0'

    # ResTable_package_header(name='test')
    package_header = b'\0\2\x20\1\x08\3\0\0\x7f\0\0\0t\0e\0s\0t\0\0\0' + \
            bytes(246) + b'\x20\1\0\0\1\0\0\0\xb4\1\0\0\4\0\0\0' + \
            b'\0\0\0\0'

    # ResStringPool
    type_strings = \
            b'\1\0\x1c\0\x94\0\0\0\x0a\0\0\0\0\0\0\0\0\1\0\0\x44\0\0\0' + \
            b'\0\0\0\0\0\0\0\0\7\0\0\0\x12\0\0\0\x1b\0\0\0\x21\0\0\0' + \
            b'\x29\0\0\0\x31\0\0\0\x3a\0\0\0\x42\0\0\0\x49\0\0\0\4\4attr\0' + \
            b'\x08\x08drawable\0\6\6layout\0\3\3raw\0\5\5color\0\5\5dimen\0' + \
            b'\6\6string\0\5\5style\0\4\4menu\0\2\2id\0' + \
            b'\0\0'

    # ResStringPool
    key_strings = \
            b'\1\0\x1c\0\x4c\0\0\0' + \
            b'\4\0\0\0\0\0\0\0\0\1\0\0\x2c\0\0\0\0\0\0\0' + \
            b'\0\0\0\0\x08\0\0\0\x11\0\0\0\x19\0\0\0' + \
            b'\5\5alarm\0\6\6alarm1\0\5\5arrow\0\4\4back\0'

    typeSpec = b'\2\2\x10\0\x20\0\0\0\7\0\0\0\4\0\0\0' + (b'\4\0\0\0' * 4) #20

    type1 = b'\1\2\x44\0\x74\0\0\0\7\0\0\0\4\0\0\0\x54\0\0\0' + \
            b'\x30\0\0\0' + bytes(0x2c) + \
            b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
            b'\x08\0\0\0\0\0\0\0\x08\0\0\0\x08\0\0\0' + \
            b'\x08\0\0\0\x11\0\0\0\x08\0\0\0\x19\0\0\0'

    type2 = b'\1\2\x44\0\x74\0\0\0\7\0\0\0\4\0\0\0\x54\0\0\0' + \
            b'\x30\0\0\0\0\0\0\0de' + bytes(0x26) + \
            b'\0\0\0\0\x10\0\0\0\x20\0\0\0\x30\0\0\0' + \
            b'\x08\0\0\0\0\0\0\0\x08\0\0\0\x08\0\0\0' + \
            b'\x08\0\0\0\x11\0\0\0\x08\0\0\0\x19\0\0\0'

    tv1_bytes = table_header + value_strings + package_header + type_strings + \
    key_strings + typeSpec + type1 + type2

    tv1_obj = \
            ResTable(
                ResTable_header(
                    ResChunk_header(
                        ResourceType.RES_TABLE_TYPE, 12, 818
                    ),
                    1
                ),
                ResStringPool(),
                [
                    ResTable_package(
                        ResTable_package_header(
                            ResChunk_header(
                                ResourceType.RES_TABLE_PACKAGE_TYPE, 288, 776
                            ),
                            127, b't\x00e\x00s\x00t\x00\x00\x00', 288, 1, 436, 4
                        ),
                        ResStringPool(
                            ResStringPool_header(
                                ResChunk_header(
                                    ResourceType.RES_STRING_POOL_TYPE, 28, 148
                                ),
                                10, 0, Flags.UTF8_FLAG, 68, 0
                            ),
                            [
                                uint32(0),
                                uint32(7),
                                uint32(18),
                                uint32(27),
                                uint32(33),
                                uint32(41),
                                uint32(49),
                                uint32(58),
                                uint32(66),
                                uint32(73)
                            ],
                            [],
                            [
                                b'\x04\x04attr\x00',
                                b'\x08\x08drawable\x00',
                                b'\x06\x06layout\x00',
                                b'\x03\x03raw\x00',
                                b'\x05\x05color\x00',
                                b'\x05\x05dimen\x00',
                                b'\x06\x06string\x00',
                                b'\x05\x05style\x00',
                                b'\x04\x04menu\x00',
                                b'\x02\x02id\x00\x00\x00'
                            ],
                            []
                        ),
                        ResStringPool(
                            ResStringPool_header(
                                ResChunk_header(
                                    ResourceType.RES_STRING_POOL_TYPE, 28, 76
                                ),
                                4, 0, Flags.UTF8_FLAG, 44, 0
                            ),
                            [
                                uint32(0),
                                uint32(8),
                                uint32(17),
                                uint32(25)
                            ],
                            [],
                            [
                                b'\x05\x05alarm\x00',
                                b'\x06\x06alarm1\x00',
                                b'\x05\x05arrow\x00',
                                b'\x04\x04back\x00'
                            ],
                            []
                        ),
                        [
                            [
                                ResTable_typeSpec(
                                    ResTable_typeSpec_header(
                                        ResChunk_header(
                                            ResourceType.RES_TABLE_TYPE_SPEC_TYPE,
                                            16, 32
                                        ),
                                        7, 0, 0, 4
                                    ),
                                    b'\x04\x00\x00\x00\x04\x00\x00\x00'\
                                            b'\x04\x00\x00\x00\x04\x00\x00\x00'
                                ),
                                ResTable_type(
                                    ResTable_type_header(
                                        ResChunk_header(
                                            ResourceType.RES_TABLE_TYPE_TYPE,
                                            68, 116
                                        ),
                                        7, 0, 0, 4, 84,
                                        b'0\x00\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00'
                                    ),
                                    b'\x00\x00\x00\x00\x10\x00\x00\x00 \x00'\
                                            b'\x00\x000\x00\x00\x00\x08\x00'\
                                            b'\x00\x00\x00\x00\x00\x00\x08\x00'\
                                            b'\x00\x00\x08\x00\x00\x00\x08\x00'\
                                            b'\x00\x00\x11\x00\x00\x00\x08\x00'\
                                            b'\x00\x00\x19\x00\x00\x00'
                                ),
                                ResTable_type(
                                    ResTable_type_header(
                                        ResChunk_header(
                                            ResourceType.RES_TABLE_TYPE_TYPE,
                                            68, 116
                                        ),
                                        7, 0, 0, 4, 84,
                                        b'0\x00\x00\x00\x00\x00\x00\x00de\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00\x00\x00\x00\x00\x00'\
                                                b'\x00\x00'
                                    ),
                                    b'\x00\x00\x00\x00\x10\x00\x00\x00 \x00'\
                                            b'\x00\x000\x00\x00\x00\x08\x00\x00'\
                                            b'\x00\x00\x00\x00\x00\x08\x00\x00'\
                                            b'\x00\x08\x00\x00\x00\x08\x00\x00'\
                                            b'\x00\x11\x00\x00\x00\x08\x00\x00'\
                                            b'\x00\x19\x00\x00\x00'
                                )
                            ]
                        ]
                    )
                ]
            )


    def test_str(self):
        invector = ResTableTests.tv1_obj
        expected = '{header={header={type=ResourceType.RES_TABLE_TYPE, ' \
                'headerSize=12, size=818}, packageCount=1}, values={header={'\
                "header={type=ResourceType.RES_STRING_POOL_TYPE, "\
                "headerSize=28, size=28}, stringCount=0, styleCount=0, "\
                "flags=Flags.0, stringsStart=0, stylesStart=0}, strrefs=[], "\
                "stylerefs=[], strings=[], styles=[]}, packages=["\
                "{header={header={type="\
                "ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=288, "\
                "size=776}, id=127, name=b't\\x00e\\x00s\\x00t\\x00\\x00\\x00"+\
                ("\\x00" * 246)+"', typeStrings=288, lastPublicType=1, "\
                "keyStrings=436, lastPublicKey=4}, typeStrings={"\
                "header={header={"\
                "type=ResourceType.RES_STRING_POOL_TYPE, headerSize=28, "\
                "size=148}, stringCount=10, styleCount=0, "\
                "flags=Flags.UTF8_FLAG, stringsStart=68, stylesStart=0}, "\
                "strrefs=[uint32(0), uint32(7), uint32(18), uint32(27), "\
                "uint32(33), uint32(41), uint32(49), uint32(58), uint32(66), "\
                "uint32(73)], stylerefs=[], strings=[b'\\x04\\x04attr\\x00', "\
                "b'\\x08\\x08drawable\\x00', b'\\x06\\x06layout\\x00', "\
                "b'\\x03\\x03raw\\x00', b'\\x05\\x05color\\x00', "\
                "b'\\x05\\x05dimen\\x00', b'\\x06\\x06string\\x00', "\
                "b'\\x05\\x05style\\x00', b'\\x04\\x04menu\\x00', "\
                "b'\\x02\\x02id\\x00\\x00\\x00'], styles=[]}, "\
                "keyStrings={header={header={"\
                "type=ResourceType.RES_STRING_POOL_TYPE, headerSize=28, "\
                "size=76}, stringCount=4, styleCount=0, "\
                "flags=Flags.UTF8_FLAG, stringsStart=44, stylesStart=0}, "\
                "strrefs=[uint32(0), uint32(8), uint32(17), uint32(25)], "\
                "stylerefs=[], strings=[b'\\x05\\x05alarm\\x00', "\
                "b'\\x06\\x06alarm1\\x00', b'\\x05\\x05arrow\\x00', "\
                "b'\\x04\\x04back\\x00'], styles=[]}, "\
                "types=[[ResTable_typeSpec(ResTable_typeSpec_header("\
                "ResChunk_header(ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32"\
                "), 7, 0, 0, 4), b'\\x04\\x00\\x00\\x00\\x04\\x00\\x00\\x00"\
                "\\x04\\x00\\x00\\x00\\x04\\x00\\x00\\x00'), ResTable_type("\
                "ResTable_type_header(ResChunk_header("\
                "ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 7, 0, 0, 4, 84, "\
                "b'0\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'"\
                "), b'\\x00\\x00\\x00\\x00\\x10\\x00\\x00\\x00 \\x00\\x00\\x00"\
                "0\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x08"\
                "\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x11"\
                "\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00'), "\
                "ResTable_type(ResTable_type_header(ResChunk_header("\
                "ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 7, 0, 0, 4, 84, "\
                "b'0\\x00\\x00\\x00\\x00\\x00\\x00\\x00de\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'), b'\\x00"\
                "\\x00\\x00\\x00\\x10\\x00\\x00\\x00 \\x00\\x00\\x000\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x08\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x11\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00')]]}]}"
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTableTests.tv1_obj
        expected = 'ResTable(ResTable_header(ResChunk_header('\
                'ResourceType.RES_TABLE_TYPE, 12, 818), 1), ResStringPool('\
                'ResStringPool_header(ResChunk_header('\
                'ResourceType.RES_STRING_POOL_TYPE, 28, 28), 0, 0, Flags.0, '\
                '0, 0), [], [], [], []), ['\
                'ResTable_package(ResTable_package_header(ResChunk_header('\
                'ResourceType.RES_TABLE_PACKAGE_TYPE, 288, 776), 127, '\
                "b't\\x00e\\x00s\\x00t\\x00\\x00\\x00"+('\\x00'*246)+\
                "', 288, 1, 436, 4), ResStringPool(ResStringPool_header("\
                'ResChunk_header(ResourceType.RES_STRING_POOL_TYPE, 28, 148), '\
                '10, 0, Flags.UTF8_FLAG, 68, 0), [uint32(0), uint32(7), '\
                'uint32(18), uint32(27), uint32(33), uint32(41), uint32(49), '\
                'uint32(58), uint32(66), uint32(73)], [], ['\
                "b'\\x04\\x04attr\\x00', b'\\x08\\x08drawable\\x00', "\
                "b'\\x06\\x06layout\\x00', b'\\x03\\x03raw\\x00', "\
                "b'\\x05\\x05color\\x00', b'\\x05\\x05dimen\\x00', "\
                "b'\\x06\\x06string\\x00', b'\\x05\\x05style\\x00', "\
                "b'\\x04\\x04menu\\x00', b'\\x02\\x02id\\x00\\x00\\x00'], "\
                "[]), ResStringPool(ResStringPool_header(ResChunk_header("\
                "ResourceType.RES_STRING_POOL_TYPE, 28, 76), 4, 0, "\
                "Flags.UTF8_FLAG, 44, 0), [uint32(0), uint32(8), uint32(17), "\
                "uint32(25)], [], [b'\\x05\\x05alarm\\x00', "\
                "b'\\x06\\x06alarm1\\x00', b'\\x05\\x05arrow\\x00', "\
                "b'\\x04\\x04back\\x00'], []), [[ResTable_typeSpec("\
                "ResTable_typeSpec_header(ResChunk_header("\
                "ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, 32), 7, 0, 0, 4), "\
                "b'\\x04\\x00\\x00\\x00\\x04\\x00\\x00\\x00\\x04\\x00\\x00"\
                "\\x00\\x04\\x00\\x00\\x00'), ResTable_type("\
                "ResTable_type_header(ResChunk_header("\
                "ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 7, 0, 0, 4, 84, "\
                "b'0\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'"\
                "), b'\\x00\\x00\\x00\\x00\\x10\\x00\\x00\\x00 \\x00\\x00\\x00"\
                "0\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x08"\
                "\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x11"\
                "\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00'), "\
                "ResTable_type(ResTable_type_header(ResChunk_header("\
                "ResourceType.RES_TABLE_TYPE_TYPE, 68, 116), 7, 0, 0, 4, 84, "\
                "b'0\\x00\\x00\\x00\\x00\\x00\\x00\\x00de\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00"\
                "\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x00'), b'\\x00"\
                "\\x00\\x00\\x00\\x10\\x00\\x00\\x00 \\x00\\x00\\x000\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x08\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x08\\x00\\x00\\x00\\x11\\x00"\
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00')]])])"
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTableTests.tv1_obj
        expected = 816
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTableTests.tv1_obj
        expected = ResTableTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTableTests.tv1_bytes + b'\x13\x37'
        expected = ResTableTests.tv1_obj, b'\x13\x37'
        actual = ResTable.from_bytes(invector)

        self.assertEqual(expected, actual)
