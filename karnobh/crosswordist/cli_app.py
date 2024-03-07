#!/usr/bin/env python3

import argparse
import os
import sys
import time

from karnobh.crosswordist.grid_generator import create_random_grid, CrossWordsIndex
from karnobh.crosswordist.words_index import WordsIndex
from karnobh.crosswordist.solution_finder import find_solution, FinderResult
from karnobh.crosswordist.grid_file_writter import write_svg

MODE_INDEX = "index"
MODE_CROSSWORD = "crossword"

ALLOWED_MODES = [MODE_INDEX, MODE_CROSSWORD]

GRID_SYMMETRY_TYPE_X = 'X'
GRID_SYMMETRY_TYPE_D = 'D'
GRID_SYMMETRY_TYPE_NO = 'NO'

ALLOWED_GRID_SYMMETRY_TYPES = [
    GRID_SYMMETRY_TYPE_X,
    GRID_SYMMETRY_TYPE_D,
    GRID_SYMMETRY_TYPE_NO,
]

COMPRESSED_INDEX_TYPE_FAST = "fast"
COMPRESSED_INDEX_TYPE_SLOW = "slow"

ALLOWED_COMPRESSED_INDEX_TYPES = [
    COMPRESSED_INDEX_TYPE_FAST,
    COMPRESSED_INDEX_TYPE_SLOW,
]

DEFAULT_GRID_SIZE = 11
DEFAULT_UNUSED_SQUARES_PERCENTAGE = 16.6
DEFAULT_SYMMETRY = "D"
DEFAULT_GRID_GENERATION_TIMEOUT_SECONDS = 3
DEFAULT_GRID_MIN_WORD_LENGTH = 3
DEFAULT_CROSSWORD_GENERATION_TIMEOUT_SECONDS = 15
DEFAULT_OUTPUT_DIRECTORY = 'out'
DEFAULT_NUMBER_OF_CROSSWORDS = 100
DEFAULT_PIXEL_SIZE = 800

ALLOWED_VERBOSITY_LEVELS = [0, 1, 2]
DEFAULT_VERBOSITY_LEVEL = 0


class AppError(Exception): ...


class App:

    MIN_ALLOWED_GRID_SIZE = 3
    MAX_ALLOWED_GRID_SIZE = 35

    MIN_ALLOWED_GRID_UNUSED_PERCENTAGE = 0
    MAX_ALLOWED_GRID_UNUSED_PERCENTAGE = 100

    MIN_ALLOWED_WORD_LEN = 3

    INDEX_CREATION_WAITING_DOTS = 15

    MIN_ALLOWED_PICTURE_PIXELS = 200

    EMPTY_GRID_LOG_MAPPING = {
        0: "□",
        1: "■",
    }

    FILLED_GRID_LOG_MAPPING = {
        0: "■",
        "": "□"
    }

    SOLUTION_RESULTS_MAPPING = {
        FinderResult.FOUND: "Found",
        FinderResult.NO_SOLUTION: "Does not exist",
        FinderResult.TIMED_OUT: "Timed Out",
    }

    RESULT_FILE_PREFIX = "crossword"

    def __init__(self,
                 mode: str,
                 index: str,
                 words_file: str,
                 grid_size: int,
                 grid_unused_percentage: float,
                 grid_symmetry: str,
                 grid_generation_timeout_seconds: float,
                 grid_min_word_length: int,
                 compressed_index_type: str,
                 crossword_generation_timeout_seconds: float,
                 output_dir: str,
                 number_of_crosswords: int,
                 picture_pixels: int,
                 verbosity: int):
        super().__init__()

        # yep, dirty and straightforward...
        if mode not in ALLOWED_MODES:
            raise ValueError(f"Provided mode {mode} is not in allowed.")

        if mode == MODE_INDEX:
            if not isinstance(words_file, str) or not words_file:
                raise ValueError(
                    f"Words file should be provided if mode '{MODE_INDEX}' is selected and be of "
                    f"appropriate type."
                )
            if not os.path.isfile(words_file):
                raise ValueError(
                    f"Words file '{words_file}' should exist if mode '{MODE_INDEX}' is selected."
                )

        if not isinstance(index, str) or not index:
            raise ValueError(f"Index should be of proper type and cannot be empty.")

        if mode == MODE_CROSSWORD and not os.path.isfile(index):
            raise ValueError(
                f"Index file: '{index}' should exist if mode: '{MODE_CROSSWORD}' is selected."
            )

        if not isinstance(grid_size, int):
            raise ValueError("Greed size is not of proper type")

        if not self.MIN_ALLOWED_GRID_SIZE <= grid_size <= self.MAX_ALLOWED_GRID_SIZE:
            raise ValueError(
                f"Grid size should be in range "
                f"[{self.MIN_ALLOWED_GRID_SIZE}, {self.MAX_ALLOWED_GRID_SIZE}]"
            )

        if not 0 <= grid_unused_percentage < 100:
            raise ValueError(
                f"Grid unused percentage should be in range "
                f"[{self.MIN_ALLOWED_GRID_UNUSED_PERCENTAGE}, "
                f"{self.MAX_ALLOWED_GRID_UNUSED_PERCENTAGE})"
            )

        if grid_symmetry not in ALLOWED_GRID_SYMMETRY_TYPES:
            raise ValueError(
                f"Grid symmetry type: {grid_symmetry} is not supported. "
                f"Supported types: {ALLOWED_GRID_SYMMETRY_TYPES}"
            )

        if (not isinstance(grid_generation_timeout_seconds, int)
                and not isinstance(grid_generation_timeout_seconds, float)):
            raise ValueError("Grid generation timeout seconds is not of correct type")

        if grid_generation_timeout_seconds < 0:
            raise ValueError("Grid generation timeout cannot be negative")

        if not isinstance(grid_min_word_length, int):
            raise ValueError("Grid minimal word length is not of correct type")

        if compressed_index_type not in ALLOWED_COMPRESSED_INDEX_TYPES:
            raise ValueError(
                f"Compressed index type {compressed_index_type} is not supported. "
                f"Supported index types: {ALLOWED_COMPRESSED_INDEX_TYPES}"
            )

        if (not isinstance(crossword_generation_timeout_seconds, float)
                and not isinstance(crossword_generation_timeout_seconds, int)):
            raise ValueError("Crossword generation timeout seconds is not of correct type")

        if crossword_generation_timeout_seconds < 0:
            raise ValueError("Crossword generation timeout seconds cannot be negative")

        if not isinstance(output_dir, str) or not output_dir:
            raise ValueError("Output directory is not of correct type or empty")

        if not isinstance(number_of_crosswords, int):
            raise ValueError("Number of crosswords is not of correct type")

        if number_of_crosswords < 1:
            raise ValueError("Number of crosswords should be a natural number")

        if not isinstance(picture_pixels, int):
            raise ValueError("Picture pixels is not of correct type")

        if picture_pixels < self.MIN_ALLOWED_PICTURE_PIXELS:
            raise ValueError(f"Wrong picture size in pixels. "
                             f"Minimal allowed picture pixels is {self.MIN_ALLOWED_PICTURE_PIXELS}")

        if verbosity not in ALLOWED_VERBOSITY_LEVELS:
            raise ValueError(f"Wrong verbosity level. Allowed: {ALLOWED_VERBOSITY_LEVELS}")

        self._mode = mode
        self._index = index
        self._words_file = words_file
        self._grid_size = grid_size
        self._grid_unused_percentage = grid_unused_percentage
        self._grid_symmetry = grid_symmetry
        self._grid_generation_timeout_seconds = grid_generation_timeout_seconds
        self._grid_min_word_length = grid_min_word_length
        self._compressed_index_type = compressed_index_type
        self._crossword_generation_timeout_seconds = crossword_generation_timeout_seconds
        self._output_dir = output_dir
        self._number_of_crosswords = number_of_crosswords
        self._picture_pixels = picture_pixels
        self._verbosity = verbosity

    def print_verbose(self, out, level, **kwargs):
        if self._verbosity >= level:
            print(out, **kwargs)

    def index_mode(self):
        words_size = os.path.getsize(self._words_file)
        chunk_size = words_size // self.INDEX_CREATION_WAITING_DOTS
        with open(self._words_file) as f:
            with WordsIndex.as_context() as wi:
                self.print_verbose("Creating index (may require several minutes)", 1, end='')
                next_chunk = chunk_size
                while True:
                    word = f.readline()
                    if not word:
                        break
                    file_pos = f.tell()
                    while file_pos > next_chunk:
                        next_chunk += chunk_size
                        self.print_verbose(".", 1, end='', flush=True)
                    wi.add_word(word.strip())
        self.print_verbose('', 1)
        with open(self._index, 'w') as f:
            wi.dump(f)

    def crossword_mode(self):
        os.makedirs(self._output_dir, exist_ok=True)
        with open(self._index) as f:
            if self._compressed_index_type == 'fast':
                try:
                    from karnobh.crosswordist.word_index_native import WordIndexNative
                    wi_loaded = WordIndexNative(file=f)
                except ImportError as ie:
                    raise AppError("Cannot load fast compressed index. (Is it compiled?). "
                                   "Try to use slow compressed index") from ie
                except (Exception,) as e:
                    raise AppError(f"Cannot load/init fast index. {str(e)}") from e
            elif self._compressed_index_type == 'slow':
                wi_loaded = WordsIndex(file=f)
            else:
                raise AppError(f"Wrong state of the system. "
                               f"Got compressed index type: '{self._compressed_index_type}'")
        found_times = 0
        total_found_secs = 0
        self.print_verbose("Starting Crosswords Generation. \n"
                           "The operation is time intensive, please be patient...", 1)
        digits_num = len(str(self._number_of_crosswords + 1))
        for num in range(1, self._number_of_crosswords + 1):
            self.print_verbose(f"Generating Crossword Number {num}", 2)
            grid = create_random_grid(
                size=self._grid_size,
                black_ratio=self._grid_unused_percentage / 100.0,
                symmetry=self._grid_symmetry,
                min_word_size=self._grid_min_word_length,
                timeout_seconds=self._crossword_generation_timeout_seconds
            )
            self.print_verbose("Generated Random Grid:", 2)
            self.print_verbose(grid.pretty_log(self.EMPTY_GRID_LOG_MAPPING), 2)
            cross_words_index = CrossWordsIndex(grid=grid)
            t0 = time.time()
            solution = find_solution(
                word_index=wi_loaded,
                cross_words_index=cross_words_index,
                timeout_after_seconds=self._crossword_generation_timeout_seconds,
            )
            solution_secs = time.time() - t0
            if solution == FinderResult.FOUND:
                found_times += 1
                total_found_secs += solution_secs
            self.print_verbose(
                f"Result: {self.SOLUTION_RESULTS_MAPPING[solution]}. "
                f"Passed time: {solution_secs} seconds. "
                f"Found ratio: {found_times / num}.",
                2
            )
            self.print_verbose(
                cross_words_index.letters_matrix.pretty_log(self.FILLED_GRID_LOG_MAPPING),
                2
            )
            file_name = f"crossword_{str(num).zfill(digits_num)}.svg"
            file_name_with_dir = os.path.join(self._output_dir, file_name)
            write_svg(
                cross_words_index=cross_words_index,
                file_name=file_name_with_dir,
                size_px=self._picture_pixels,
            )
        self.print_verbose(
            f"Found solutions number: {found_times}.",
            1
        )
        if found_times > 0:
            average_time = total_found_secs / found_times
            self.print_verbose(f"Average time per found solution: {average_time}", 1)


    def run(self):
        mode_mapping = {
            MODE_INDEX: self.index_mode,
            MODE_CROSSWORD: self.crossword_mode
        }
        mode_mapping[self._mode]()


def main():
    prog_name = "crosswordist"
    parser = argparse.ArgumentParser(
        prog=prog_name,
        description="Generate random crosswords.",
        epilog=f"Examples:\n"
               f"  ### Generate index from the provided file of words. ###\n"
               f"  {prog_name} -m {MODE_INDEX} -i words_index.json\n\n"
               f"  ### Generate crosswords from the provided index. ###\n"
               f"  {prog_name} -i words_index.json\n",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        '-m',
        '--mode',
        choices=ALLOWED_MODES,
        default=MODE_CROSSWORD,
        help=f"Working mode. '{MODE_INDEX}' - generate index file of words. "
             f"'{MODE_CROSSWORD}' - generate crossword."
    )

    parser.add_argument(
        '-i',
        '--index',
        required=True,
        help=f"In '{MODE_INDEX}' mode - output file for generated index."
             f"In '{MODE_CROSSWORD}' mode - input index file."
    )

    parser.add_argument(
        '-wf',
        '--words-file',
        help=f"File of words (words expected to be in upper case). "
             f"If mode: '{MODE_INDEX}' is selected then this argument is mandatory."
    )

    parser.add_argument(
        '-gsi',
        '--grid-size',
        default=DEFAULT_GRID_SIZE,
        type=int,
        help=f"Size of generated crossword grid. Default {DEFAULT_GRID_SIZE}."
    )

    parser.add_argument(
        '-gu',
        '--grid-unused-percentage',
        type=float,
        default=DEFAULT_UNUSED_SQUARES_PERCENTAGE,
        help=f"Percentage of space which is not used in grid (I.e., black squares). "
             f"Default {DEFAULT_UNUSED_SQUARES_PERCENTAGE}."
    )

    parser.add_argument(
        '-gsy',
        '--grid-symmetry',
        choices=ALLOWED_GRID_SYMMETRY_TYPES,
        default=GRID_SYMMETRY_TYPE_D,
        help=f"Symmetry type of generated grid. "
             f"'{GRID_SYMMETRY_TYPE_X}' - both diagonals. "
             f"'{GRID_SYMMETRY_TYPE_D}' - one diagonal. "
             f"'{GRID_SYMMETRY_TYPE_NO}' - asymmetrical. "
             f"Default '{GRID_SYMMETRY_TYPE_D}'."
    )

    parser.add_argument(
        '-gto',
        '--grid-generation-timeout-seconds',
        type=float,
        default=DEFAULT_GRID_GENERATION_TIMEOUT_SECONDS,
        help=f"Timeout for the grid layout (geometry) generation "
             f"(E.g., too dense unused cells percentage specified). "
             f"Default {DEFAULT_GRID_GENERATION_TIMEOUT_SECONDS}."
    )

    parser.add_argument(
        '-gw',
        '--grid-min-word-length',
        type=int,
        default=DEFAULT_GRID_MIN_WORD_LENGTH,
        help=f"Minimal length of the word in grid. Default {DEFAULT_GRID_MIN_WORD_LENGTH}."
    )

    parser.add_argument(
        '-cit',
        '--compressed-index-type',
        choices=ALLOWED_COMPRESSED_INDEX_TYPES,
        default=COMPRESSED_INDEX_TYPE_FAST,
        help=f"Compressed index type. "
             f"'{COMPRESSED_INDEX_TYPE_FAST}' - C based index (should be compiled). "
             f"'{COMPRESSED_INDEX_TYPE_SLOW}' - Python based index."
    )

    parser.add_argument(
        '-cgt',
        '--crossword-generation-timeout-seconds',
        type=float,
        default=DEFAULT_CROSSWORD_GENERATION_TIMEOUT_SECONDS,
        help=f"Timeout for the crossword generation (finding suitable words in cells). "
             f"Default {DEFAULT_CROSSWORD_GENERATION_TIMEOUT_SECONDS}."
    )

    parser.add_argument(
        '-o',
        '--output-dir',
        default=DEFAULT_OUTPUT_DIRECTORY,
        help=f"Output directory to store generated results. "
             f"Default '{DEFAULT_OUTPUT_DIRECTORY}'."
    )

    parser.add_argument(
        '-nc',
        '--number-of-crosswords',
        type=int,
        default=DEFAULT_NUMBER_OF_CROSSWORDS,
        help=f"Number of crosswords to be generated. Default: {DEFAULT_NUMBER_OF_CROSSWORDS}."
    )

    parser.add_argument(
        '-pp',
        '--picture-pixels',
        type=int,
        default=DEFAULT_PIXEL_SIZE,
        help=f"Size of result crossword picture in pixels. "
             f"Default: {DEFAULT_PIXEL_SIZE}."
    )

    parser.add_argument(
        '-v',
        '--verbosity',
        type=int,
        choices=ALLOWED_VERBOSITY_LEVELS,
        default=DEFAULT_VERBOSITY_LEVEL,
        help=f"Verbosity level. Available levels: {', '.join(map(str, ALLOWED_VERBOSITY_LEVELS))}. "
             f"Default: {DEFAULT_VERBOSITY_LEVEL}."
    )

    args = parser.parse_args()
    args_dict = vars(args)
    try:
        app = App(**args_dict)
        app.run()
    except (Exception,) as e:
        print(str(e), file=sys.stderr)


if __name__ == '__main__':
    main()

