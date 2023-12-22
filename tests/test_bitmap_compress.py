import unittest
from karnobh.crosswordist.bitmap import compress, CompressedBitmap, bit_index


class MyTestCase(unittest.TestCase):

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

    def test_bit_index_generic(self):
        t = 'FF' * 32
        byte_seq = bytearray.fromhex(t)
        expected = [n for n in range(32 * 8)]
        actual = [bi for bi in bit_index(byte_sequence=byte_seq)]
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
