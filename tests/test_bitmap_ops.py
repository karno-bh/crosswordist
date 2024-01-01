import unittest
import operator

from karnobh.crosswordist.bitmap import (and_all, or_all, CompressedBitmap, make_op_all, MakeOpError,
                                         NotEnoughSequencesError, bit_op_index2, CompressedBitmap2)


class BitmapOpsTestCase(unittest.TestCase):

    def setUp(self):
        t = ['00ff00ff00ff',
             'f0000f000f00',
             '0f00f000f000']
        self.seqs = [bytearray.fromhex(seq_str) for seq_str in t]
        self.compressed_seqs = [CompressedBitmap(bs) for bs in self.seqs]

    def test_simple_or(self):
        expected = bytearray.fromhex('ffffffffffff')
        actual = bytearray([b for b in or_all(*self.seqs)])
        self.assertEqual(expected, actual)

    def test_simple_and(self):
        expected = bytearray.fromhex('000000000000')
        actual = bytearray([b for b in and_all(*self.seqs)])
        self.assertEqual(expected, actual)

    def test_compressed_or(self):
        expected = bytearray.fromhex('ffffffffffff')
        actual = bytearray([b for b in or_all(*self.compressed_seqs)])
        self.assertEqual(expected, actual)

    def test_compressed_and(self):
        expected = bytearray.fromhex('000000000000')
        actual = bytearray([b for b in and_all(*self.compressed_seqs)])
        self.assertEqual(expected, actual)

    def test_raising_not_make_op_error(self):
        self.assertRaises(MakeOpError, make_op_all, None)

    def test_make_op_not_enough_sequences_and_or(self):
        self.assertRaises(NotEnoughSequencesError, lambda: [b for b in and_all(self.compressed_seqs[0])])
        self.assertRaises(NotEnoughSequencesError, lambda: [b for b in or_all(self.compressed_seqs[0])])


class CompressedBitmapOpsTestCase(unittest.TestCase):

    def test_simple_seek(self):
        t = ['000000ff00ff',
             '00000ff00f00',
             '0000f0f0f000']
        self.seqs = [bytearray.fromhex(seq_str) for seq_str in t]
        self.compressed_seqs = [CompressedBitmap2(bs) for bs in self.seqs]
        expected = [24, 25, 26, 27]
        actual =  [x for x in bit_op_index2(*self.compressed_seqs, op=operator.and_)]
        self.assertEqual(expected, actual)
