import unittest
from karnobh.crosswordist.bitmap import compress


class MyTestCase(unittest.TestCase):

    def test_simple_compress(self):
        t = '00' * (8191 * 2 + 8190)
        res = compress(bytearray.fromhex(t))
        # print([bin(b) for b in r])
        expected = ['0x3f', '0xff', '0x3f', '0xff', '0x3f', '0xfe']
        self.assertEqual(expected, [hex(b) for b in res])


if __name__ == '__main__':
    unittest.main()
