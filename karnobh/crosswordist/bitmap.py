"""
This module aggregates functionality to create and manipulate compressed byte sequences. The
compression is done by simplified RLE encoding. Contiguous segments of 0x00 or 0xFF bytes are
prepended by a control byte (or two)which encode the following length. Segments of bytes non-zero or
0xFF bytes are also prepended by a control byte (or two) which encode the following length. Segments
of 0x00 or 0xFF are called "fill bytes", segments of other bytes are called "noise bytes".

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

import operator
import functools


def compress(byte_sequence) -> bytearray:
    """ This function compresses the byte sequence by the simplified algorithm

    :param byte_sequence: the sequence of incoming bytes
    :return: compressed byte sequence

    See module description for the algorithm
    """
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
                    fill_seq_control_bytes = ((0x2000 | (fill_bit << 14)) | fb_cnt).to_bytes(
                        2,
                        'big')
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


FILL_TYPES = [0x00, 0xFF]


class CompressedBitmap:
    """
    Simplified class wrapper for the byte sequence for decoding purposes of compressed
    byte sequence.

    Examples:
        >>> bs = bytearray.fromhex("0000FFFF8888")
        >>> bytearray(x for x in CompressedBitmap(bs)) == bs
        True
    """

    def __init__(self, byte_sequence):
        super().__init__()
        self._compressed_seq = compress(byte_sequence)

    def __iter__(self):
        seq = self._compressed_seq
        fill_types = FILL_TYPES
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


class CompressedBitmap2:
    """
    This class is a wrapper for decoding compressed byte sequence. In addition, the iterator
    returned by this class can seek its position forward if required. This feature is useful
    when the bitmap is needed to be sought. For example, in the AND operation of multiple bitmap
    indexes, if there is contiguous sequence of zeroes in one of them, all others may be sought
    in the number of such zeroes.

    Examples:
        >>> bs = bytearray.fromhex("000000FFFF8888")
        >>> cbmp = CompressedBitmap2(bs)
        >>> bytearray(b for b in cbmp) == bs
        True
        >>> iter(cbmp).seekable_bytes
        3
        >>> icbmp = iter(cbmp)
        >>> icbmp.seek(icbmp.seekable_bytes)
        >>> next(icbmp)
        255
    """

    class CompressedBitmap2Iter:

        def __init__(self, compressed_seq):
            super().__init__()
            self._compressed_seq = compressed_seq
            self._compressed_byte_index = 0
            self._is_noise = None
            self._fill_type = None
            self._remaining_bytes = 0
            self._read_control_byte()
            self._stop_on_next_iter = False

        @property
        def seekable_bytes(self):
            if self._is_noise or self._fill_type == 0xFF:
                return 0
            return self._remaining_bytes

        def _read_control_byte(self):
            if self._compressed_byte_index >= len(self._compressed_seq):
                self._stop_on_next_iter = True
                return
            byte = self._compressed_seq[self._compressed_byte_index]
            self._is_noise = byte >> 7
            if self._is_noise:
                bytes_count = byte & 0x3F
                is_long = (byte >> 6) & 1
                if is_long:
                    self._compressed_byte_index += 1
                    bytes_count = ((bytes_count << 8) |
                                   self._compressed_seq[self._compressed_byte_index])
                self._compressed_byte_index += 1
            else:
                self._fill_type = FILL_TYPES[byte >> 6]
                bytes_count = byte & 0x1F
                is_long = (byte >> 5) & 1
                if is_long:
                    self._compressed_byte_index += 1
                    bytes_count = ((bytes_count << 8) |
                                   self._compressed_seq[self._compressed_byte_index])
                self._compressed_byte_index += 1
            self._remaining_bytes = bytes_count

        def seek(self, bytes_to_seek):
            while self._remaining_bytes < bytes_to_seek:
                bytes_to_seek -= self._remaining_bytes
                if self._is_noise:
                    self._compressed_byte_index += self._remaining_bytes
                self._read_control_byte()
            self._remaining_bytes -= bytes_to_seek
            if self._is_noise:
                self._compressed_byte_index += bytes_to_seek
            if self._remaining_bytes == 0:
                self._read_control_byte()

        def __next__(self):
            if self._stop_on_next_iter:
                raise StopIteration()
            if self._is_noise:
                ret_val = self._compressed_seq[self._compressed_byte_index]
            else:
                ret_val = self._fill_type
            self.seek(1)
            return ret_val

    def __init__(self, byte_sequence, compressed_sequence=None):
        super().__init__()
        if compressed_sequence is None:
            self._compressed_seq = compress(byte_sequence)
        else:
            self._compressed_seq = compressed_sequence

    def __iter__(self):
        return self.CompressedBitmap2Iter(compressed_seq=self._compressed_seq)

    @property
    def compressed_sequence(self):
        return bytes(self._compressed_seq)


def bit_index(byte_sequence):
    """ Converts byte sequence bits into the sequential bit number if it is on.

    :param byte_sequence: any byte-like sequence
    :return: Sequence of integers which are turned on bits in byte sequence bits

    Examples:
        >>> bs = bytearray.fromhex("001F01")
        >>> list(bit_index(bs))
        [11, 12, 13, 14, 15, 23]
    """
    for byte_index, byte in enumerate(byte_sequence):
        for bit_num in range(7, -1, -1):
            if (byte >> bit_num) & 1:
                yield byte_index * 8 + (7 - bit_num)


def bit_index2(byte_sequence):
    byte_index = 0
    bs_iter = iter(byte_sequence)
    while (byte := next(bs_iter, None)) is not None:
        if byte == 0:
            seekable_bytes = getattr(bs_iter, 'seekable_bytes', 0)
            if seekable_bytes > 0:
                # print("seekable bytes: ", seekable_bytes)
                byte_index += seekable_bytes
                bs_iter.seek(seekable_bytes)
        if byte != 0:
            for bit_num in range(7, -1, -1):
                if (byte >> bit_num) & 1:
                    yield byte_index * 8 + (7 - bit_num)
        byte_index += 1


class MakeOpError(Exception):
    pass


class NotEnoughSequencesError(Exception):
    pass


class UnsupportedOperator(Exception):
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


OP_TO_BEHAVIOR = {
    operator.and_: max,
    operator.or_: min,
}


def bit_op_index2(*byte_sequences, op=None):
    """ Combines byte sequences by provided operator and returns indexes of bits in the sequence

    If the iterator of the sequence supports seeking forward bytes by having the "seekable_bytes"
    property, the logic of function will seek forward number of bytes that may be sought. For the
    AND operation the number of bytes that may be bypassed is the maximum number of zero bytes among
    all sequences. For the OR operation the minimal number of zero bytes may be sought. There is no
    reason for seeking ones in the OR operation since the function returns indexes of turned on
    bits, and thus they turned on bits should be reported anyway.

    :param byte_sequences: at least 2 byte sequences
    :param op: operator from the built-in operator module: only or_(), and_() supported
    :return: Sequence of integers for which are turned on bits in the hypothetical bits of combined
             by operator input byte sequences

    Examples:
        >>> hex_sequences = ["00 00 01", "FF FF FF", "88 88 8F"]
        >>> compressed_sequences = [CompressedBitmap2(bytearray.fromhex(s)) for s in hex_sequences]
        >>> list(bit_op_index2(*compressed_sequences, op=operator.and_))
        [23]
        >>> list(bit_op_index2(*compressed_sequences, op=operator.or_)) == list(range(3*8))
        True
        >>> list(bit_op_index2(compressed_sequences))
        Traceback (most recent call last):
        ...
        karnobh.crosswordist.bitmap.MakeOpError: Operator is not defined
        >>> list(bit_op_index2(compressed_sequences[0], op=operator.and_))
        Traceback (most recent call last):
        ...
        karnobh.crosswordist.bitmap.NotEnoughSequencesError: Not enough byte sequences
        >>> list(bit_op_index2(*compressed_sequences, op=operator.xor))
        Traceback (most recent call last):
        ...
        karnobh.crosswordist.bitmap.UnsupportedOperator: Cannot process with operator: <built-in function xor>
    """
    if op is None:
        raise MakeOpError("Operator is not defined")
    if len(byte_sequences) < 2:
        raise NotEnoughSequencesError("Not enough byte sequences")

    behavior_op = OP_TO_BEHAVIOR.get(op)
    if behavior_op is None:
        raise UnsupportedOperator(f"Cannot process with operator: {op}")

    byte_index = 0
    bs_iters = [iter(bs) for bs in byte_sequences]
    while True:
        main_byte, *other_bytes = [next(i, None) for i in bs_iters]
        if main_byte is None:
            break
        byte = functools.reduce(op, other_bytes, main_byte)
        all_merged_bytes = functools.reduce(operator.or_, other_bytes, main_byte)
        if all_merged_bytes == 0:
            seekable_bytes = behavior_op(*(getattr(ibs, 'seekable_bytes', 0) for ibs in bs_iters))
            if seekable_bytes > 0:
                # print(f"seeking {seekable_bytes} bytes")
                byte_index += seekable_bytes
                for ibs in bs_iters:
                    ibs.seek(seekable_bytes)
        if byte != 0:
            for bit_num in range(7, -1, -1):
                if (byte >> bit_num) & 1:
                    yield byte_index * 8 + (7 - bit_num)
        byte_index += 1


def bool_to_byte_bits_seq(seq):
    """ Converts sequence of True/False values into the byte sequence
    If sequence is not exact byte alligned (i.e., not divisible by 8), LSB of last bytes returned
    as 0 bit.

    :param seq: sequence of the True/False values
    :return: sequence of bytes where True/False converted to bits

    Examples:
        >>> s = [1, 1, 1, 1,  0, 0, 0, 0,  0, 0, 0, 1]
        >>> list(bool_to_byte_bits_seq(s)) == [0xF0, 0x10]
        True
    """
    result, cnt = 0, 0
    for value in seq:
        result |= bool(value)
        cnt += 1
        if cnt == 8:
            yield result
            result, cnt = 0, 0
        else:
            result <<= 1
    yield result << (7 - cnt)
