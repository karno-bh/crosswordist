from contextlib import contextmanager
import operator
import json
import base64
import logging


from karnobh.crosswordist.bitmap import (CompressedBitmap2, bool_to_byte_bits_seq, bit_index2,
                                         bit_op_index2)

logger = logging.getLogger(__name__)


class WordsIndexWrongLen(Exception):
    pass


class NotSupportTypeItem(Exception):
    pass


class IndexAlreadyConstructed(Exception):
    pass


class WordsIndexSameLen:

    def __init__(self, length, alphabet=None, words=None, bitmap_index=None):
        super().__init__()
        if not isinstance(length, int) or length < 2:
            raise WordsIndexWrongLen(
                "The length of word should be integer and at least 2 letters"
            )
        if alphabet is None:
            logger.debug("The alphabet is not provided. Latin alphabet will be used.")
            alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self._abc = alphabet

        self._length = length
        self._bitmap_index = bitmap_index
        self._words = words or set()

    def __len__(self):
        return self._length

    @property
    def words(self):
        return self._words  # list(self._words) ???

    def add_word(self, word) -> bool:
        if len(word) != self._length:
            raise WordsIndexWrongLen(f"Word: {word} is not of required length {self._length}")
        if self._bitmap_index is not None:
            raise IndexAlreadyConstructed("Index is already constructed, "
                                          "cannot add more words")
        if next((ltr for ltr in word if ltr not in self._abc), None) is not None:
            logger.debug("Word %s is not in the abc '%s'", word, self._abc)
            return False
        self._words.add(word)
        return True

    def make_index(self):
        if self._bitmap_index is not None:
            raise IndexAlreadyConstructed("Index is already constructed")
        self._words = sorted(self._words)
        self._bitmap_index = []
        for i in range(self._length):
            letter_index = {}
            for abc_letter in self._abc:
                # the list is faster than iterator, i.e.
                # letter_seq = (w[i] == abc_letter for w in self._words)
                letter_seq = [w[i] == abc_letter for w in self._words]
                abc_letter_bitmap = CompressedBitmap2(
                    byte_sequence=bool_to_byte_bits_seq(
                        letter_seq
                    )
                )
                letter_index[abc_letter] = abc_letter_bitmap
            self._bitmap_index.append(letter_index)

    def bitmap_on_position(self, letter_index, letter):
        return self._bitmap_index[letter_index][letter]

    def word_at(self, word_index):
        return self._words[word_index]

    def as_human_readable_dict(self):
        encoded_bm_index = []
        for pos in self._bitmap_index:
            letter_index = {}
            for letter, index in pos.items():
                encoded = base64.b64encode(index.compressed_sequence)
                letter_index[letter] = encoded.decode('ASCII')
            encoded_bm_index.append(letter_index)
        return {
            'words': self._words,
            'index': encoded_bm_index,
            'abc': self._abc,
        }

    def __getitem__(self, item):
        match item:
            case int():
                return self.word_at(item)
            case slice():
                return self.bitmap_on_position(item.start, item.stop)
            case _:
                raise NotSupportTypeItem(f"Type {type(item)} is not supported")

    @staticmethod
    @contextmanager
    def as_context(length):
        words_index = WordsIndexSameLen(length)
        yield words_index
        words_index.make_index()


class WordsIndex:

    def __init__(self, alphabet: list[str] | None = None,
                 length_range: range | None = None,
                 file=None):
        super().__init__()
        self._words_index = {}
        if file is None:
            self._alphabet = alphabet
            if not length_range:
                length_range = range(3, 37)
                logger.debug("Length range is not provided, using the default range: (%s, %s)",
                             length_range.start, length_range.stop)
            self._length_range: range = length_range
            self._index_constructed = False
        else:
            words_index = json.load(file)
            range_start, range_stop = words_index['range']
            self._length_range = range(range_start, range_stop)
            del words_index['range']
            for length_str, index_by_word_length in words_index.items():
                len_int = int(length_str)
                words = index_by_word_length['words']
                encoded_index = index_by_word_length['index']
                abc = index_by_word_length['abc']
                bitmap_index = []
                for letter_pos in encoded_index:
                    bitmap_index_on_pos = {}
                    for letter, encoded_letter_index in letter_pos.items():
                        bitmap_index_on_pos[letter] = CompressedBitmap2(
                            byte_sequence=None,
                            compressed_sequence=base64.b64decode(encoded_letter_index)
                        )
                    bitmap_index.append(bitmap_index_on_pos)
                self._words_index[len_int] = WordsIndexSameLen(
                    length=len_int,
                    alphabet=abc,
                    words=words,
                    bitmap_index=bitmap_index
                )
            self._index_constructed = True

    def add_word(self, word):
        if self._index_constructed:
            raise IndexAlreadyConstructed("Index is already constructed. Cannot add more words.")
        word_len = len(word)
        if word_len not in self._length_range:
            logger.debug("Word's '%s' length='%s' is not in allowed(%s, %s)",
                         word, word_len, self._length_range.start, self._length_range.stop)
            return
        index_by_length = self._words_index.get(word_len)
        if index_by_length is None:
            index_by_length = WordsIndexSameLen(
                length=word_len,
                alphabet=self._alphabet
            )
            self._words_index[word_len] = index_by_length
        index_by_length.add_word(word)

    def make_index(self):
        if self._index_constructed:
            raise IndexAlreadyConstructed("Index is already constructed")
        # indexes = [index for index in self._words_index.values()]
        # random.shuffle(indexes)
        # cpus_num = os.cpu_count()
        # jobs = [indexes[i:i + cpus_num] for i in range(0, len(indexes), cpus_num)]
        # with ThreadPoolExecutor(max_workers=cpus_num) as thread_pool:
        #     results = thread_pool.map(
        #         lambda _indexes: [(index, index.make_index()) for index in _indexes],
        #         jobs
        #     )
        # for indexes in results:
        #     # print(indexes)
        #     logger.debug("WordIndexSameLen %s indexes finished",
        #                  [len(i[0]) for i in indexes])
        for index in self._words_index.values():
            index.make_index()

    def word_index_by_length(self, length):
        return self._words_index[length]

    def __getitem__(self, item):
        return self.word_index_by_length(item)

    def dump(self, file):
        word_index = {}
        for length, index in self._words_index.items():
            word_index[length] = index.as_human_readable_dict()
        word_index['range'] = [self._length_range.start, self._length_range.stop]
        json.dump(word_index, file, indent=2)

    def _perform_lookup(self, length, mapping, op=None):
        if op is None:
            op = operator.and_
        words_index_same_len = self.word_index_by_length(length)
        byte_sequences = [words_index_same_len.bitmap_on_position(pos, letter)
                          for pos, letter in mapping.items()]
        arr_index_stream = bit_op_index2(*byte_sequences, op=op)\
            if len(byte_sequences) != 1 else bit_index2(byte_sequences[0])
        return arr_index_stream, words_index_same_len

    def lookup(self, length, mapping, op=None):
        arr_index_stream, words_index_same_len = self._perform_lookup(length, mapping, op)
        for arr_index in arr_index_stream:
            yield words_index_same_len._words[arr_index]

    def count_occurrences(self, length, mapping, op=None):
        arr_index_stream, _ = self._perform_lookup(length, mapping, op)
        return sum(1 for _ in arr_index_stream)

    def does_intersection_exist(self, length, mapping, op=None):
        arr_index_stream, _ = self._perform_lookup(length, mapping, op)
        return any(True for _ in arr_index_stream)

    @staticmethod
    @contextmanager
    def as_context():
        words_index = WordsIndex()
        yield words_index
        words_index.make_index()
