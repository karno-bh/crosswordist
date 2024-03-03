from karnobh.crosswordist.grid_generator import CrossWordsIndex
from collections import namedtuple
from karnobh.crosswordist.graphics import Rect, Text, Translate, EmitterContext, GraphicsEmitter

CrosswordGraphicsObjects = namedtuple("CrosswordGraphicsObjects",
                                      ("cells", "numbers", "letters"))


def emit_graphics_objects(cross_word_index: CrossWordsIndex,
                          size_px: int) -> CrosswordGraphicsObjects:
    grid_w, grid_h = cross_word_index.grid.size
    cell_size_px = size_px // grid_w
    cells_rects = []
    for x in range(grid_w):
        cell_x_coord = x * cell_size_px
        for y in range(grid_h):
            cell_y_coord = y * cell_size_px
            grid_val = cross_word_index.grid.get(x, y)
            cells_rects.append(Rect(x=cell_x_coord,
                                    y=cell_y_coord,
                                    w=cell_size_px,
                                    h=cell_size_px,
                                    context=EmitterContext(
                                       fill="white" if not grid_val else "black",
                                       # stroke="black" if not grid_val else "white",
                                       mergeable=True
                                    )))

    word_nums = {(w.word_num, w.x_init, w.y_init) for w in cross_word_index.all}
    number_size = cell_size_px // 10
    number_size = round(number_size * 1.5)
    numbers_text = []
    for word_num in word_nums:
        n, x, y = word_num
        text = str(n + 1)
        cell_x_coord = x * cell_size_px
        cell_y_coord = y * cell_size_px
        number_text_x = cell_x_coord + number_size // 2
        number_text_y = cell_y_coord + number_size
        numbers_text.append(Text(x=number_text_x,
                                 y=number_text_y,
                                 text=text,
                                 font_size=number_size,
                                 text_anchor="start",
                                 ))
    letter_matrix = cross_word_index.letters_matrix
    letters = []
    for x in range(grid_w):
        cell_x_coord = x * cell_size_px
        for y in range(grid_h):
            matrix_val = letter_matrix.get(x, y)
            if matrix_val in (0, ""):
                continue
            cell_y_coord = y * cell_size_px
            letter_x_coord = cell_x_coord + cell_size_px // 2
            letter_y_coord = cell_y_coord + cell_size_px - round(cell_size_px * 0.10)
            letter_size = round(cell_size_px * 0.85)
            letters.append(Text(x=letter_x_coord,
                                y=letter_y_coord,
                                text=matrix_val,
                                font_size=letter_size,
                                text_anchor="middle"))

    return CrosswordGraphicsObjects(
        cells=cells_rects,
        numbers=numbers_text,
        letters=letters
    )


def draw_crossword(cross_word_index: CrossWordsIndex,
                   graphics_emitter: GraphicsEmitter,
                   size_px=600):
    rects, numbers, letters = emit_graphics_objects(cross_word_index, size_px)
    graphics_emitter.push_context(
        context=EmitterContext(
            stroke_width=2,
            stroke="black",
        )
    )
    for rect in rects:
        rect.emit(graphics_emitter)
    graphics_emitter.pop_context()
    graphics_emitter.push_context(EmitterContext())
    for num in numbers:
        num.emit(graphics_emitter)
    for letter in letters:
        letter.emit(graphics_emitter)
