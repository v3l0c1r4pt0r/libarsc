#!/usr/bin/env python3
## \file uint32.py
#  \brief Unsigned 32-bit Integer
import struct
import unittest

class uint32:

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
        return struct.pack("%sI" % self._endian, int(self.integer))

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
        integer, = struct.unpack("%sI" % _endian, b[:4])
        return uint32(integer, little), b[4:]

class uint32Tests(unittest.TestCase):

    def test_bytes(self):
        invector = uint32(0x1234567, little=True)
        expected = b'\x67\x45\x23\x01'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\x67\x45\x23\x01\x13\x37'
        expected = uint32(0x1234567), b'\x13\x37'
        actual = uint32.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = uint32(0xffffffff) # TODO: same for 0 and 1
        expected = 4
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = uint32(0xdeadbeef)
        expected = 'uint32(3735928559)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = uint32(0xdeadbeef)
        expected = '3735928559'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes_passes_endianness(self):
        invector = b'\1\0\0\0'
        expected = invector
        obj, b = uint32.from_bytes(invector, little=True)
        actual = bytes(obj)

        self.assertEqual(expected, actual)
