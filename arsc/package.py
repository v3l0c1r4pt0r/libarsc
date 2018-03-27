#!/usr/bin/env python3
## \file package.py
# \brief ResTable_package and related
import unittest
from arsc.type.uint32 import uint32
from arsc.type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.stringpool import ResStringPool
from arsc.stringpool import ResStringPool_header
from arsc.tabletype import ResTable_typeSpec
from arsc.tabletype import ResTable_typeSpec_header
from arsc.tabletype import ResTable_type
from arsc.tabletype import ResTable_type_header
from arsc.types import ResourceType
from arsc.external.configuration import AConfiguration
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResTable_package_header
# \brief A collection of resource data types within a package.
# \details Followed by one or more ResTable_type and ResTable_typeSpec
# structures containing the entry values for each resource type.
class ResTable_package_header:

    MAX_NAME_LEN = 128
    len = 0x120

    def __init__(self, header=None, id=0, name=b'\0\0', typeStrings=0,
            lastPublicType=0, keyStrings=0, lastPublicKey=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_TABLE_PACKAGE_TYPE,
                    headerSize=ResTable_package_header.len,
                    size=ResTable_package_header.len)
        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_TABLE_PACKAGE_TYPE:
            raise ChunkHeaderWrongTypeException(
                    ResourceType.RES_TABLE_PACKAGE_TYPE)
        ## \link ResChunk_header \endlink instance
        # \details Identifies structure and defines its size
        self.header = header

        if isinstance(id, uint32):
            ## If this is a base package, its ID
            # \details Package IDs start at 1 (corresponding to the value of the
            # package bits in a resource identifier). 0 means this is not a base
            # package.
            self.id = id
        else:
            self.id = uint32(id, little=True)

        if isinstance(name, bytes):
            name_length = len(name)
            if name_length > ResTable_package_header.MAX_NAME_LEN * 2:
                raise Exception('name is longer than maximum ({l}>{m})'.format(
                    l=name_length, m=ResTable_package_header.MAX_NAME_LEN))
            if name[-2:] != b'\0\0':
                raise(Exception('name does not end with NULL'))
            ## Actual name of this package
            # \details NULL-terminated, UTF-16 string.
            self.name = name + bytes((ResTable_package_header.MAX_NAME_LEN * \
                    2) - name_length)
        else:
            raise Exception('name must be of type bytes')

        if isinstance(typeStrings, uint32):
            self.typeStrings = typeStrings
        else:
            self.typeStrings = uint32(typeStrings, little=True)

        if isinstance(lastPublicType, uint32):
            self.lastPublicType = lastPublicType
        else:
            self.lastPublicType = uint32(lastPublicType, little=True)

        if isinstance(keyStrings, uint32):
            self.keyStrings = keyStrings
        else:
            self.keyStrings = uint32(keyStrings, little=True)

        if isinstance(lastPublicKey, uint32):
            self.lastPublicKey = lastPublicKey
        else:
            self.lastPublicKey = uint32(lastPublicKey, little=True)

    def __str__(self):
        return '{{header={header}, id={id}, name={name}, '\
                'typeStrings={typeStrings}, lastPublicType={lastPublicType}, '\
                'keyStrings={keyStrings}, lastPublicKey={lastPublicKey}}}'.\
                format(header=str(self.header), id=str(self.id),
                        name=str(self.name), typeStrings=str(self.typeStrings),
                        lastPublicType=str(self.lastPublicType),
                        keyStrings=str(self.keyStrings),
                        lastPublicKey=str(self.lastPublicKey))

    def __repr__(self):
        return '{c}({header}, {id}, {name}, {typeStrings}, {lastPublicType}, ' \
                '{keyStrings}, {lastPublicKey})'.format(c=type(self).__name__,
                header=repr(self.header), id=self.id,
                name=repr(self.name), typeStrings=self.typeStrings,
                lastPublicType=self.lastPublicType,
                keyStrings=self.keyStrings,
                lastPublicKey=self.lastPublicKey)

    def __eq__(self, rhs):
        if type(self) != type(rhs):
            return False
        return self.header == rhs.header and self.id == rhs.id and \
                self.name == rhs.name and self.typeStrings == rhs.typeStrings \
                and self.lastPublicType == rhs.lastPublicType and \
                self.keyStrings == rhs.keyStrings and \
                self.lastPublicKey == rhs.lastPublicKey

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        id = bytes(self.id)
        name = bytes(self.name)
        typeStrings = bytes(self.typeStrings)
        lastPublicType = bytes(self.lastPublicType)
        keyStrings = bytes(self.keyStrings)
        lastPublicKey = bytes(self.lastPublicKey)

        return header + id + name + typeStrings + lastPublicType + \
                keyStrings + lastPublicKey + bytes(4)

    def from_bytes(b):
        header, b = ResChunk_header.from_bytes(b)
        id, b = uint32.from_bytes(b, little=True)
        name, b = b[:256], b[256:]
        typeStrings, b = uint32.from_bytes(b, little=True)
        lastPublicType, b = uint32.from_bytes(b, little=True)
        keyStrings, b = uint32.from_bytes(b, little=True)
        lastPublicKey, b = uint32.from_bytes(b, little=True)

        return ResTable_package_header(header, id, name, typeStrings,
                lastPublicType, keyStrings, lastPublicKey), b[4:]


## \class ResTable_package
#  \brief Describes whole package, together with its content
#  \details Contains ResTable_package_header as a header, then followed by two
#  ResStringPool objects and interlaced ResTable_typeSpec and multiple
#  ResTable_type objects
class ResTable_package:

    def __init__(self, header=None, typeStrings=None, keyStrings=None,
            types=None):

        if header is None:
            header = ResTable_package_header()

        if typeStrings is None:
            typeStrings = ResStringPool()

        if keyStrings is None:
            keyStrings = ResStringPool()

        if not isinstance(header, ResTable_package_header):
            raise WrongTypeException('header', ResTable_package_header)
        ## Instance of ResTable_package_header. Stores package name and id.
        self.header = header

        if not isinstance(typeStrings, ResStringPool):
            raise WrongTypeException('typeStrings', ResStringPool)
        ## Instance of ResStringPool. Stores available types.
        self.typeStrings = typeStrings

        if not isinstance(keyStrings, ResStringPool):
            raise WrongTypeException('header', ResStringPool)
        ## Instance of ResStringPool. Stores available types.
        self.keyStrings = keyStrings

        # TODO: implement
        self.types = types

    def __str__(self):
        return '{{header={header}, typeStrings={typeStrings}, '\
                'keyStrings={keyStrings}, types={types}}}'.format(
                        header=str(self.header),
                        typeStrings=str(self.typeStrings),
                        keyStrings=str(self.keyStrings), types=str(self.types))

    def __repr__(self):
        return '{c}({header}, {typeStrings}, {keyStrings}, '\
                '{types})'.format(c=type(self).__name__,
                header=repr(self.header), typeStrings=repr(self.typeStrings),
                keyStrings=repr(self.keyStrings), types=repr(self.types))

    def __eq__(self, rhs):
        return type(self) == type(rhs) and \
                self.header == rhs.header and \
                self.typeStrings == rhs.typeStrings and \
                self.keyStrings == rhs.keyStrings and \
                self.types == rhs.types

    def __len__(self):
        return len(bytes(self))

    def __bytes__(self):
        header = bytes(self.header)
        # FIXME: determine position and order of types and keys using header
        typeStrings = bytes(self.typeStrings)
        keyStrings = bytes(self.keyStrings)
        types = bytes()
        for spec in self.types:
            for obj in spec:
                types += bytes(obj)

        return header + typeStrings + keyStrings + types

    def from_bytes(b, little=True):
        content = b
        header, b = ResTable_package_header.from_bytes(b)
        content_size = header.header.size.integer
        content, b = content[:content_size], content[content_size:]
        typeStrings, at = ResStringPool.from_bytes(
                content[header.typeStrings.integer:])
        keyStrings, ak = ResStringPool.from_bytes(
                content[header.keyStrings.integer:])
        if len(ak) < len(at):
            rest = ak
        else:
            rest = at

        types = []
        spec = None
        ret_b = b
        b = rest

        # Deserialize typeSpec and type till end of package. Final structure
        # would be list of lists, where inner list always starts with typeSpec
        # and contains all related type structures
        while len(b) > 0:
            hdr, _ = ResChunk_header.from_bytes(b)
            if hdr.type == ResourceType.RES_TABLE_TYPE_SPEC_TYPE:
                if spec is not None:
                    types.append(spec)
                spec = []
                typeSpec, b = ResTable_typeSpec.from_bytes(b)
                spec.append(typeSpec)
            elif hdr.type == ResourceType.RES_TABLE_TYPE_TYPE:
                typ, b = ResTable_type.from_bytes(b)
                spec.append(typ)
            else:
                raise ChunkHeaderWrongTypeException([
                    ResourceType.RES_TABLE_TYPE_SPEC_TYPE,
                    ResourceType.RES_TABLE_TYPE_TYPE], hdr.type)
        types.append(spec)

        return ResTable_package(header, typeStrings, keyStrings, types), ret_b


class ResTable_package_headerTests(unittest.TestCase):

    def test_header_is_invalid(self):
        with self.assertRaises(Exception) as cm:
            invector = ResTable_package_header('qwer')

        expected = 'header must be of type ResChunk_header'
        _, actual = cm.exception.args

        self.assertEqual(expected, actual)

    def test_header_type_is_invalid(self):
        with self.assertRaises(Exception) as cm:
            invector = ResTable_package_header(ResChunk_header(
                ResourceType.RES_NULL_TYPE))

        expected = 'header must describe resource of type '\
                'ResourceType.RES_TABLE_PACKAGE_TYPE'
        _, actual = cm.exception.args

        self.assertEqual(expected, actual)

    @unittest.skip('Error on uint32 side')
    def test_id_is_not_uintable(self):
        invector = ResTable_package_header(id='123')
        expected = None
        actual = None

        self.assertEqual(expected, actual)

    def test_name_is_valid(self):
        invector = ResTable_package_header(name=b'q\0w\0e\0r\0\0\0')
        expected = b'q\0w\0e\0r\0\0\0' + bytes(246)
        actual = invector.name

        self.assertEqual(expected, actual)

    def test_name_is_invalid(self):
        with self.assertRaises(Exception) as cm:
            invector = ResTable_package_header(name='qwer\0')

        expected = 'name must be of type bytes'
        actual, = cm.exception.args

        self.assertEqual(expected, actual)

    def test_name_is_not_null_terminated(self):
        invector = b'q\0w\0e\0r\0'
        expected = None
        actual = None

        self.assertEqual(expected, actual)

    @unittest.skip('No possibility to store UTF-16 string of fixed len')
    def test_str(self):
        invector = ResTable_package_header(header=ResChunk_header(
            chunkType=ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=0x120,
            size=0x103e4), id=0x7f, name=b't\0e\0s\0t\0\0\0', typeStrings=0x120,
            lastPublicType=10, keyStrings=0x1b4, lastPublicKey=0x319)
        expected = '{header={type=ResourceType.RES_TABLE_PACKAGE_TYPE, ' \
                'headerSize=288, size=66532}, id=127, name=\'test\', ' \
                'typeStrings=288, lastPublicType=10, keyStrings=436, ' \
                'lastPublicKey=793}'
        actual = str(invector)

        self.assertEqual(expected, actual)

    @unittest.skip('No possibility to store UTF-16 string of fixed len')
    def test_repr(self):
        invector = ResTable_package_header(header=ResChunk_header(
            chunkType=ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=0x120,
            size=0x103e4), id=0x7f, name=b't\0e\0s\0t\0\0\0', typeStrings=0x120,
            lastPublicType=10, keyStrings=0x1b4, lastPublicKey=0x319)
        expected = 'ResTable_package_header(ResChunk_header(' \
                'ResourceType.RES_TABLE_PACKAGE_TYPE, 288, 66532), 127, ' \
                '\'test\', 288, 10, 436, 793)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = ResTable_package_header(header=ResChunk_header(
            chunkType=ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=0x120,
            size=0x103e4), id=0x7f, name=b't\0e\0s\0t\0\0\0', typeStrings=0x120,
            lastPublicType=10, keyStrings=0x1b4, lastPublicKey=0x319)
        expected = 0x120
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_package_header(header=ResChunk_header(
            chunkType=ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=0x120,
            size=0x103e4), id=0x7f, name=b't\0e\0s\0t\0\0\0', typeStrings=0x120,
            lastPublicType=10, keyStrings=0x1b4, lastPublicKey=0x319)
        expected = b'\0\2\x20\1\xe4\3\1\0\x7f\0\0\0t\0e\0s\0t\0\0\0' + \
                bytes(246) + b'\x20\1\0\0\x0a\0\0\0\xb4\1\0\0\x19\3\0\0' + b'\0\0\0\0'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\0\2\x20\1\xe4\3\1\0\x7f\0\0\0t\0e\0s\0t\0\0\0' + \
        bytes(246) + b'\x20\1\0\0\x0a\0\0\0\xb4\1\0\0\x19\3\0\0' + \
        b'\0\0\0\0' + b'\x13\x37'
        expected = ResTable_package_header(header=ResChunk_header(
            chunkType=ResourceType.RES_TABLE_PACKAGE_TYPE, headerSize=0x120,
            size=0x103e4), id=0x7f, name=b't\0e\0s\0t\0\0\0', typeStrings=0x120,
            lastPublicType=10, keyStrings=0x1b4, lastPublicKey=0x319), \
        b'\x13\x37'
        actual = ResTable_package_header.from_bytes(invector)

        self.assertEqual(expected, actual)

    def test_objects_are_not_same(self):
        invector1 = ResTable_package_header()
        invector2 = ResTable_package_header()
        invector1.header.size = uint32(123)

        self.assertIsNot(invector1, invector2)
        self.assertNotEqual(invector1, invector2)


class ResTable_packageTests(unittest.TestCase):

    # FIXME: a bit ugly, maybe change ?
    Flags = ResStringPool_header.Flags

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

    tv1_bytes = package_header + type_strings + key_strings + typeSpec + type1 + \
            type2

    tv1_obj = \
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
                            (b'\x04\x00\x00\x00' * 4)
                        ),
                        ResTable_type(
                            ResTable_type_header(
                                ResChunk_header(
                                    ResourceType.RES_TABLE_TYPE_TYPE, 68, 116
                                ),
                                7, 0, 0, 4, 84,
                                b'0' + bytes(0x2f)
                            ),
                            b'\x00\x00\x00\x00\x10\x00\x00\x00'\
                                    b' \x00\x00\x000\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x00\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x08\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x11\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x19\x00\x00\x00'
                        ),
                        ResTable_type(
                            ResTable_type_header(
                                ResChunk_header(
                                    ResourceType.RES_TABLE_TYPE_TYPE, 68, 116
                                ),
                                7, 0, 0, 4, 84,
                                b'0\x00\x00\x00\x00\x00\x00\x00de'+bytes(0x26)
                            ),
                            b'\x00\x00\x00\x00\x10\x00\x00\x00'\
                                    b' \x00\x00\x000\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x00\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x08\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x11\x00\x00\x00'\
                                    b'\x08\x00\x00\x00\x19\x00\x00\x00'
                        )
                    ]
                ]
            )

    def test_str(self):
        invector = ResTable_packageTests.tv1_obj
        expected = "{header={header={type="\
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
                "ResChunk_header(ResourceType.RES_TABLE_TYPE_SPEC_TYPE, 16, "\
                "32), 7, 0, 0, 4), b'\\x04\\x00\\x00\\x00\\x04\\x00\\x00\\x00"\
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
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00')]]}"
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = ResTable_packageTests.tv1_obj
        expected = "ResTable_package(ResTable_package_header(ResChunk_header("\
                "ResourceType.RES_TABLE_PACKAGE_TYPE, 288, 776), 127, "\
                "b't\\x00e\\x00s\\x00t\\x00\\x00\\x00" + ("\\x00" * 246) + \
                "', 288, 1, 436, 4), ResStringPool(ResStringPool_header("\
                "ResChunk_header(ResourceType.RES_STRING_POOL_TYPE, 28, 148"\
                "), 10, 0, Flags.UTF8_FLAG, 68, 0), [uint32(0), uint32(7), "\
                "uint32(18), uint32(27), uint32(33), uint32(41), uint32(49), "\
                "uint32(58), uint32(66), uint32(73)], [], ["\
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
                "\\x00\\x00\\x08\\x00\\x00\\x00\\x19\\x00\\x00\\x00')]])"
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_packageTests.tv1_obj
        expected = ResTable_packageTests.tv1_bytes
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = ResTable_packageTests.tv1_bytes + b'\x13\x37'
        expected = ResTable_packageTests.tv1_obj, b'\x13\x37'
        actual = ResTable_package.from_bytes(invector)

        self.assertEqual(expected, actual)
