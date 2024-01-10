import unittest
from karnobh.crosswordist.bitmap import (compress, CompressedBitmap, CompressedBitmap2, bit_index,
                                         bit_index2, bool_to_byte_bits_seq)


class CompressedBitmapTestCase(unittest.TestCase):

    def test_simple_compress(self):
        t = '00' * (8191 * 2 + 8190)
        res = compress(bytearray.fromhex(t))
        # print([bin(b) for b in r])
        expected = ['0x3f', '0xff', '0x3f', '0xff', '0x3f', '0xfe']
        self.assertEqual(expected, [hex(b) for b in res])

    def test_bytes_in_iter(self):
        t = '00' * (8191 * 2 + 10)
        # res = compress(bytearray.fromhex(t))
        original = bytearray.fromhex(t)
        cb = CompressedBitmap(byte_sequence=original)
        uncompressed = bytearray()
        for b in cb:
            uncompressed.append(b)
        self.assertEqual(uncompressed, original)

    def test_bytes_in_iter_complex(self):
        t = ('00' * (8191 + 66)) + ('1f' * (8191 + 66)) + ('11' * (8191 + 66)) + ('FF' * (8191 * 2 + 44))
        # t = ('1f' * (8191 + 66)) + ('11' * (8191 + 66))
        original = bytearray.fromhex(t)
        cb = CompressedBitmap(byte_sequence=original)
        # print("Compressed Ratio: ", cb.compressed_ratio)
        uncompressed = bytearray()
        for b in cb:
            uncompressed.append(b)
        self.assertEqual(uncompressed, original)

    def test_bit_index_simple(self):
        t = '00000000000000000000000088'
        byte_seq = bytearray.fromhex(t)
        expected = [96, 100]
        actual = [bi for bi in bit_index(byte_seq)]
        self.assertEqual(expected, actual)

    def test_bit_index2_simple(self):
        t = '00000000000000000000000088'
        byte_seq = bytearray.fromhex(t)
        expected = [96, 100]
        actual = [bi for bi in bit_index2(byte_seq)]
        self.assertEqual(expected, actual)

    def test_bit_index2_simple_compressed(self):
        t = '00000000000000000000000088'
        byte_seq = CompressedBitmap2(bytearray.fromhex(t))
        expected = [96, 100]
        actual = [bi for bi in bit_index2(byte_seq)]
        self.assertEqual(expected, actual)

    def test_bit_index_generic(self):
        t = 'FF' * 32
        byte_seq = bytearray.fromhex(t)
        expected = [n for n in range(32 * 8)]
        actual = [bi for bi in bit_index(byte_sequence=byte_seq)]
        self.assertEqual(expected, actual)

    def test_bool_to_byte_bits_seq(self):
        l = [0, 0, 0, 0, 0, 0, 0, 0,
             1, 1, 1, 1, 1, 1, 1, 1,
             0, 0, 0, 0, 1, 1, 1, 1,
             0, 0, 0, 0, 1, 1, 1, 1,
             1, 1, 1, 0]
        # l = [0, 0, 0, 0, 0, 0, 0, 1,
        #      1, 1, 1, 0, 1]
        bytes_seq = bool_to_byte_bits_seq(l)
        expected = [0x0, 0xff, 0xf, 0xf, 0xe0]
        actual = [b for b in bytes_seq]
        self.assertEqual(expected, actual)

    def test_compressed_bitmap_seek_by_iteration(self):
        t = '8888FFFF44440000FFFF88'
        byte_seq = bytearray.fromhex(t)
        actual = bytearray()
        for x in CompressedBitmap2(byte_sequence=byte_seq):
            actual.append(x)
        self.assertEqual(byte_seq, actual)

    def test_compressed_bitmap_seek_simple(self):
        t = '8888FFFF44440000FFFF88'
        byte_seq = bytearray.fromhex(t)
        i = iter(CompressedBitmap2(byte_sequence=byte_seq))
        actual = next(i)
        self.assertEqual(0x88, actual)
        i.seek(3)
        actual = next(i)
        self.assertEqual(0x44, actual)

    def test_seekable_bytes(self):
        t = '000000008888'
        byte_seq = bytearray.fromhex(t)
        bm = CompressedBitmap2(byte_sequence=byte_seq)
        i = iter(bm)
        # print(i.seekable_bytes)
        actual_seekable_bytes = i.seekable_bytes
        self.assertEqual(4, actual_seekable_bytes)
        next(i)
        # print(i.seekable_bytes)
        actual_seekable_bytes = i.seekable_bytes
        self.assertEqual(3, actual_seekable_bytes)
        i.seek(i.seekable_bytes)
        # print(next(i))
        # print(next(i))
        expected_last_vals = [0x88, 0x88]
        actual_last_vals = [next(i), next(i)]
        self.assertEqual(expected_last_vals, actual_last_vals)

    def test_long_sequences_seekable_bytes(self):
        t = '00' * 8191
        for x in range(0, 20000, 500):
            tt = t + '88' * x
            bm = CompressedBitmap2(byte_sequence=bytearray.fromhex(tt))
            i = iter(bm)
            i.seek(i.seekable_bytes)
            cnt = 0
            while next(i,None) is not None:
                cnt += 1
            self.assertEqual(x, cnt)

    def test_long_sequences_seekable_bytes_mix(self):
        t = '00' * 8191
        for x in range(0, 20000, 500):
            tt = t + '88' * x + t + '88' * x
            bm = CompressedBitmap2(byte_sequence=bytearray.fromhex(tt))
            i = iter(bm)
            i.seek(i.seekable_bytes)
            cnt = 0
            while i.seekable_bytes == 0:
                next(i)
                cnt += 1
            i.seek(i.seekable_bytes)
            while i.seekable_bytes == 0:
                el = next(i, None)
                if el is None:
                    break
                cnt += 1
            self.assertEqual(x * 2, cnt)
