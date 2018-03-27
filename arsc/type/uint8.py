#!/usr/bin/env python3
## \file uint8.py
#  \brief Unsigned 8-bit Integer
import struct
import unittest

class uint8:

    def __init__(self, integer, little=False):
        self.little = little
        if little:
            self._endian = '<'
        else:
            self._endian = '>'
        self.integer = integer

    def __eq__(self, rhs):
        return self.integer == rhs.integer

    def __bytes__(self):
        return struct.pack("%sB" % self._endian, int(self.integer))[-1:]

    def __str__(self):
        return "%d" % self.integer

    def __repr__(self):
        return '{c}({int})'.format(c=type(self).__name__, int=self.integer)

    def __len__(self):
        return len(bytes(self))

    def from_bytes(b, little=False):
        if little:
            _endian = '<'
        else:
            _endian = '>'
        integer, = struct.unpack("%sB" % _endian,b[:1])
        return uint8(integer), b[1:]

class uint8Tests(unittest.TestCase):

    def test_bytes(self):
        invector = uint8(0xf8, little=True)
        expected = b'\xf8'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\xf8\x13\x37'
        expected = uint8(0xf8), b'\x13\x37'
        actual = uint8.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = uint8(0xff) # TODO: same for 0 and 1
        expected = 1
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = uint8(0x42)
        expected = 'uint8(66)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = uint8(0x42)
        expected = '66'
        actual = str(invector)

        self.assertEqual(expected, actual)
