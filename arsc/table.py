#!/usr/bin/env python3
## \file table.py
# \brief ResTable and related
import unittest
from type.uint32 import uint32
from type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.types import ResourceType
from arsc.external.configuration import AConfiguration
from exceptions import WrongTypeException
from exceptions import ChunkHeaderWrongTypeException

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

    len = 0x1c

    def __init__(self, header=None, packageCount=0):
        if header is None:
            header = ResChunk_header(ResourceType.RES_TABLE_TYPE,
                    headerSize=ResTable_header.len, size=ResTable_header.len)
        if not isinstance(header, ResChunk_header):
            raise WrongTypeException('header', ResChunk_header)
        if header.type is not ResourceType.RES_TABLE_TYPE:
            raise ChunkHeaderWrongTypeException(ResourceType.RES_TABLE_TYPE)
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
        # break circular dependency
        import arsc.stringpool
        ResStringPool = arsc.stringpool.ResStringPool

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

        return header

    def from_bytes(b, little=True):
        # break circular dependency
        import arsc.stringpool
        ResStringPool = arsc.stringpool.ResStringPool

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
        types = rest # TODO: implement typeSpec and type container

        return ResTable_package(header, typeStrings, keyStrings, types), b


## \class ResTable_config
#\brief Describes current ResTable_type configuration
class ResTable_config:

    def __init__(self, size=0x30, imsi=None, locale=None, screenType=None,
            input=None, screenSize=None, version=None, screenConfig=None,
            screenSizeDp=None):
        if isinstance(size, uint32):
            ## Number of bytes in this structure
            self.size = size
        else:
            self.size = uint32(size, little=True)

        self.notimpl = bytes(self.size.integer - 4)

    def __eq__(self, rhs):
        return type(self) == type(rhs) and self.size == rhs.size

    def __bytes__(self):
        size = bytes(self.size)

        return size + self.notimpl

    def from_bytes(b):
        size, b = uint32.from_bytes(b, little=True)
        restlen = size.integer - len(size)
        notimpl, b = b[:restlen], b[restlen:] # TODO: implement

        obj = ResTable_config(size)
        obj.notimpl = notimpl

        return obj, b

    ## \class Imsi
    # \brief Filter based on MCC and MNC
    class Imsi:

        def __init__(self, mcc=0, mnc=0):
            if isinstance(mcc, uint16):
                ## Mobile Country Code
                self.mcc = mcc

            if isinstance(mnc, uint16):
                ## Mobile Network Code
                self.mnc = mnc

    ## \class Locale
    # \brief Filter based on language and country
    class Locale:

        def __init__(self, language=b'\0\0', country=b'\0\0'):
            pass

    class ScreenType:
        pass

    class Input:
        pass

    class ScreenSize:
        pass

    class Version:
        pass

    class ScreenConfig:
        pass

    class ScreenSizeDp:
        pass

    ## \enum Config
    # \brief Flag bits for ResTable_typeSpec entries
    class Config(Flag):
        CONFIG_MCC = AConfiguration.ACONFIGURATION_MCC
        CONFIG_MNC = AConfiguration.ACONFIGURATION_MCC
        CONFIG_LOCALE = AConfiguration.ACONFIGURATION_LOCALE
        CONFIG_TOUCHSCREEN = AConfiguration.ACONFIGURATION_TOUCHSCREEN
        CONFIG_KEYBOARD = AConfiguration.ACONFIGURATION_KEYBOARD
        CONFIG_KEYBOARD_HIDDEN = AConfiguration.ACONFIGURATION_KEYBOARD_HIDDEN
        CONFIG_NAVIGATION = AConfiguration.ACONFIGURATION_NAVIGATION
        CONFIG_ORIENTATION = AConfiguration.ACONFIGURATION_ORIENTATION
        CONFIG_DENSITY = AConfiguration.ACONFIGURATION_DENSITY
        CONFIG_SCREEN_SIZE = AConfiguration.ACONFIGURATION_SCREEN_SIZE
        CONFIG_SMALLEST_SCREEN_SIZE = AConfiguration.ACONFIGURATION_SMALLEST_SCREEN_SIZE
        CONFIG_VERSION = AConfiguration.ACONFIGURATION_VERSION
        CONFIG_SCREEN_LAYOUT = AConfiguration.ACONFIGURATION_SCREEN_LAYOUT
        CONFIG_UI_MODE = AConfiguration.ACONFIGURATION_UI_MODE
        CONFIG_LAYOUTDIR = AConfiguration.ACONFIGURATION_LAYOUTDIR
        CONFIG_MAX = 0xffffffff

#       def from_bytes(b, little=True):
#           return Flag.from_bytes(b, True)


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

        expected = 'header must describe resource of type RES_TABLE_TYPE'
        _, actual = cm.exception.args

        self.assertEqual(expected, actual)

    def test_packageCount_is_uint32(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE), uint32(0x8331337))
        expected = uint32
        actual = type(invector.packageCount)

        self.assertEqual(expected, actual)

    def test_packageCount_is_uintable(self):
        invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE), 0x8331337)
        expected = uint32
        actual = type(invector.packageCount)

        self.assertEqual(expected, actual)

    @unittest.skip('Not working because of uint32 error')
    def test_packageCount_is_not_uintable(self):
        with self.assertRaises(TypeError) as cm:
            invector = ResTable_header(ResChunk_header(ResourceType.RES_TABLE_TYPE), 'be elite')

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

        expected = 'header must describe resource of type RES_TABLE_PACKAGE_TYPE'
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
    # break circular dependency
    import arsc.stringpool
    ResStringPool = arsc.stringpool.ResStringPool
    ResStringPool_header = arsc.stringpool.ResStringPool_header
    Flags = arsc.stringpool.ResStringPool_header.Flags


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
            type2 + b'\x13\x37'

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
                typeSpec + type1 + type2
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
                "types=" + \
                str(ResTable_packageTests.typeSpec +
                        ResTable_packageTests.type1 +
                        ResTable_packageTests.type2) + \
                "}"
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
                "b'\\x04\\x04back\\x00'], []), " + \
                repr(ResTable_packageTests.typeSpec +
                        ResTable_packageTests.type1 +
                        ResTable_packageTests.type2) + \
                ")"
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        self.maxDiff = None

        invector = ResTable_packageTests.tv1_bytes
        expected = ResTable_packageTests.tv1_obj, b'\x13\x37'
        actual = ResTable_package.from_bytes(invector)

        self.assertEqual(expected, actual)

class ResTable_configTests(unittest.TestCase):

    def test_serial_deserial(self):
        # TODO: remove as soon as bytes/from_bytes are ready
        invector = b'\x30' + bytes(7) + b'de' + bytes(38) + b'\x13\x37'
        expected = invector[:-2], b'\x13\x37'
        obj, b = ResTable_config.from_bytes(invector)
        actual = bytes(obj), b

        self.assertEqual(expected, actual)

    @unittest.skip('Not ready yet')
    def test_from_bytes(self):
        invector = b'\x30' + bytes(7) + b'de' + bytes(38) + b'\x13\x37'
        expected = ResTable_config(size=0x30,
                locale=ResTable_config.Locale(language='de')), b'\x13\x37'
        actual = ResTable_config.from_bytes(invector)

        self.assertEqual(expected, actual)

    def test_config_to_int(self):
        invector = ResTable_config.Config.CONFIG_MCC
        expected = 0x1
        actual = int(invector)

        self.assertEqual(expected, actual)

    def test_configs_sum_to_int(self):
        invector = ResTable_config.Config.CONFIG_DENSITY | \
                ResTable_config.Config.CONFIG_VERSION
        expected = 0x500
        actual = int(invector)

        self.assertEqual(expected, actual)

    def test_config_from_bytes(self):
        invector = b'\0\5\0\0\x13\x37'
        expected = ResTable_config.Config.CONFIG_DENSITY | \
                ResTable_config.Config.CONFIG_VERSION, b'\x13\x37'
        actual = ResTable_config.Config.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_bytes(self):
        invector = ResTable_config.Config.CONFIG_DENSITY | \
                ResTable_config.Config.CONFIG_VERSION
        expected = b'\0\5\0\0'
        actual = bytes(reversed(bytes(invector)))

        self.assertEqual(expected, actual)
