#!/usr/bin/env python3
## \file config.py
# \brief ResTable_config and related
import unittest
from arsc.type.uint32 import uint32
from arsc.type.flag import Flag
from arsc.chunk import ResChunk_header
from arsc.types import ResourceType
from arsc.external.configuration import AConfiguration
from arsc.exceptions import WrongTypeException
from arsc.exceptions import ChunkHeaderWrongTypeException

## \class ResTable_config
#\brief Describes current ResTable_type configuration
class ResTable_config:

    def __init__(self, size=0x30, imsi=None, locale=None, screenType=None,
            input=None, screenSize=None, version=None, screenConfig=None,
            screenSizeDp=None):
        notimpl = None
        if isinstance(size, uint32):
            ## Number of bytes in this structure
            self.size = size
        elif isinstance(size, bytes):
            # TODO: remove after full implementation
            self.size, notimpl = uint32.from_bytes(size, little=True)
        else:
            self.size = uint32(size, little=True)

        if notimpl is None:
            notimpl = bytes(self.size.integer - 4)
        self.notimpl = notimpl

    def __eq__(self, rhs):
        return type(self) == type(rhs) and self.size == rhs.size

    def __str__(self):
        # TODO: implement
        return '{size}'.\
                format(size=bytes(self.size)+self.notimpl)

    def __repr__(self):
        return '{size}'.format(size=bytes(self.size)+self.notimpl)

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
