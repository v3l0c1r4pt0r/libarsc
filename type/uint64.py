#!/usr/bin/env python3
## \file uint64.py
#  \brief Unsigned 64-bit Integer
import struct
import unittest

class uint64:

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
        return struct.pack("%sQ" % self._endian, int(self.integer))

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
        integer, = struct.unpack("%sQ" % _endian, b[:8])
        return uint64(integer, little), b[8:]

class uint64Tests(unittest.TestCase):

    def test_bytes(self):
        invector = uint64(0x123456789abcdef, little=True)
        expected = b'\xef\xcd\xab\x89\x67\x45\x23\x01'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\xef\xcd\xab\x89\x67\x45\x23\x01\x13\x37'
        expected = uint64(0x123456789abcdef), b'\x13\x37'
        actual = uint64.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = uint64(0xffffffffffffffff) # TODO: same for 0 and 1
        expected = 8
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = uint64(0xdeadbeef15431337)
        expected = 'uint64(16045690981454123831)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = uint64(0xdeadbeef15431337)
        expected = '16045690981454123831'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes_passes_endianness(self):
        invector = b'\0\1\2\3\4\5\6\7'
        expected = invector
        obj, b = uint64.from_bytes(invector, little=True)
        actual = bytes(obj)

        self.assertEqual(expected, actual)
