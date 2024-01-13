import test_bytearray001
x = [bytearray.fromhex('aabbcc00ff'), bytearray.fromhex('aacc00ff')]
test_bytearray001.test_iterable_of_buffers(x)
test_bytearray001.test_iterable_of_buffers(32)
# x = bytearray.fromhex("00aabbff")
# test_bytearray001.test_bytearray001(bytearray.fromhex('00ffaaff'))
