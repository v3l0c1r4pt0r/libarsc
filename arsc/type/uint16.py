#!/usr/bin/env python3
## \file uint16.py
#  \brief Unsigned 16-bit Integer
import struct
import unittest

class uint16:

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
        return struct.pack("%sH" % self._endian, int(self.integer))

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
        integer, = struct.unpack("%sH" % _endian,b[:2])
        return uint16(integer, little), b[2:]

class uint16Tests(unittest.TestCase):

    def test_bytes(self):
        invector = uint16(0x123, little=True)
        expected = b'\x23\x01'
        actual = bytes(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes(self):
        invector = b'\x23\x01\x13\x37'
        expected = uint16(0x123), b'\x13\x37'
        actual = uint16.from_bytes(invector, little=True)

        self.assertEqual(expected, actual)

    def test_len(self):
        invector = uint16(0xffff) # TODO: same for 0 and 1
        expected = 2
        actual = len(invector)

        self.assertEqual(expected, actual)

    def test_repr(self):
        invector = uint16(0x1337)
        expected = 'uint16(4919)'
        actual = repr(invector)

        self.assertEqual(expected, actual)

    def test_str(self):
        invector = uint16(0x1337)
        expected = '4919'
        actual = str(invector)

        self.assertEqual(expected, actual)

    def test_from_bytes_passes_endianness(self):
        invector = b'\1\0'
        expected = invector
        obj, b = uint16.from_bytes(invector, little=True)
        actual = bytes(obj)

        self.assertEqual(expected, actual)
