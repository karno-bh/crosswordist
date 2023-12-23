import operator
import functools
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


def compress(byte_sequence):
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
                    noise_seq_control_bytes = (0xC000 | nb_cnt).to_bytes(2, 'big')
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

    for byte in byte_sequence:
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

    FILL_TYPES = [0x00, 0xFF]

    def __init__(self, byte_sequence):
        super().__init__()
        self._uncompressed_len = len(byte_sequence)
        self._compressed_seq = compress(byte_sequence)
        self._compress_ratio = self._uncompressed_len / len(self._compressed_seq)

    @property
    def compressed_ratio(self):
        return self._compress_ratio

    def __iter__(self):
        seq = self._compressed_seq
        fill_types = self.FILL_TYPES
        byte_index = 0
        while byte_index < len(seq):
            byte = seq[byte_index]
            is_noise = byte >> 7
            if is_noise:
                noise_bytes_cnt = byte & 0x3F
                is_long = (byte >> 6) & 1
                if is_long:
                    byte_index += 1
                    noise_bytes_cnt = (noise_bytes_cnt << 8) | seq[byte_index]
                byte_index += 1  # first noise byte in noise sequence
                first_non_noise_byte_idx = byte_index + noise_bytes_cnt
                while byte_index < first_non_noise_byte_idx:
                    yield seq[byte_index]
                    byte_index += 1
            else:
                # fill sequence
                fill_type = fill_types[byte >> 6]  # no need for masking, MSB is zero
                fill_bytes_cnt = byte & 0x1F
                is_long = (byte >> 5) & 1
                if is_long:
                    byte_index += 1
                    fill_bytes_cnt = (fill_bytes_cnt << 8) | seq[byte_index]
                for _ in range(fill_bytes_cnt):
                    yield fill_type
                byte_index += 1


def bit_index(byte_sequence):
    for byte_index, byte in enumerate(byte_sequence):
        for bit_num in range(7, -1, -1):
            if (byte >> bit_num) & 1:
                yield byte_index * 8 + (7 - bit_num)


class MakeOpError(Exception):
    pass


class NotEnoughSequencesError(Exception):
    pass


def make_op_all(op=None):
    if op is None:
        raise MakeOpError("Operator is not defined")

    def op_all(*byte_sequences):
        if len(byte_sequences) < 2:
            raise NotEnoughSequencesError("Not enough byte sequences")
        for main_byte, *other_bytes in zip(*byte_sequences):
            yield functools.reduce(op, other_bytes, main_byte)

    return op_all


and_all = make_op_all(op=operator.and_)
or_all = make_op_all(op=operator.or_)
