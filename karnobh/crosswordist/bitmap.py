
"""
Encoding Scheme:

0XXX XXXX -> Start of fill bytes:
  00XX XXXX -> Fill bytes are zeros
  01XX XXXX -> Fill bytes are ones
  0Y0X XXXX -> Short sequence
  0Y1X XXXX XXXX XXXX -> Long sequence
1XXX XXXX -> Start of noise bytes
  10XX XXXX -> Short sequence
  11XX XXXX XXXX XXXX -> Long sequence
"""


def compress(bit_sequence: bytearray):
    fill_byte_type = 0
    fill_byte_count = 0
    noise_bytes = bytearray()
    compressed_seq = bytearray()

    def emmit_noise_bytes():
        while nb_cnt := len(noise_bytes):
            if nb_cnt > 16383:
                noise_seq_control_bytes = bytes.fromhex('FF FF')
                compressed_seq.extend(noise_seq_control_bytes)
                compressed_seq.extend(noise_bytes[:16383])
                del noise_bytes[:16383]  # does performance suffer?..
            else:
                if nb_cnt > 63:
                    noise_seq_control_bytes = (0xC000 | nb_cnt).to_bytes(2,'big')
                else:
                    noise_seq_control_bytes = (0x80 | nb_cnt).to_bytes(1, 'big')
                compressed_seq.extend(noise_seq_control_bytes)
                compressed_seq.extend(noise_bytes)
                del noise_bytes[:nb_cnt]

    def emmit_fill_bytes():
        fb_cnt = fill_byte_count
        fill_bit = fill_byte_type & 1
        while fb_cnt:
            if fb_cnt > 8191:
                fill_seq_control_bytes = 0x3FFF | (fill_bit << 14)
                compressed_seq.extend(fill_seq_control_bytes.to_bytes(2,
                                                                      'big'))
                fb_cnt -= 8191
            else:
                if fb_cnt > 31:
                    fill_seq_control_bytes = ((0x2000 | (fill_bit << 14)) | fb_cnt).to_bytes(2, 'big')
                else:
                    fill_seq_control_bytes = ((fill_bit << 6) | fb_cnt).to_bytes(1,
                                                                                 'big')
                compressed_seq.extend(fill_seq_control_bytes)
                fb_cnt -= fb_cnt

    for byte in bit_sequence:
        if byte == 0x00 or byte == 0xFF:
            if noise_bytes:
                emmit_noise_bytes()
            if fill_byte_count == 0:
                fill_byte_type = byte
                fill_byte_count = 1
            elif fill_byte_type != byte:
                emmit_fill_bytes()
                fill_byte_type = byte
                fill_byte_count = 1
            else:
                fill_byte_count += 1
        else:
            if fill_byte_count != 0:
                emmit_fill_bytes()
                fill_byte_count = 0
            noise_bytes.append(byte)
    if noise_bytes:
        emmit_noise_bytes()
    elif fill_byte_count != 0:
        emmit_fill_bytes()
    return compressed_seq


class CompressedBitmap:

    def __init__(self, bit_sequence):
        super().__init__()


def test001():
    r = compress(bytearray.fromhex('010203040506FFFFFFFFFFFFFF'))
    print(r)

    r = compress(bytearray.fromhex('00 00 00 00 00 0F 0F 0F 0F FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF FF'))
    print([hex(b) for b in r])

    t = '00' * (8191 * 2 + 8190)
    r = compress(bytearray.fromhex(t))
    print([bin(b) for b in r])
    print([hex(b) for b in r])


def main():
    test001()


if __name__ == '__main__':
    main()
