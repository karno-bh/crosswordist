from karnobh.crosswordist.grid_generator import CrossWordsIndex
from karnobh.crosswordist.grid_emitter import draw_crossword
from karnobh.crosswordist.graphics import SvgGraphicsEmitter


def write_svg(cross_words_index: CrossWordsIndex, file_name, size_px):
    with open(file_name, 'w') as f:
        print(f'<svg width="{size_px}" height="{size_px}" xmlns="http://www.w3.org/2000/svg">',
              file=f)
        emitter = SvgGraphicsEmitter(f)
        draw_crossword(cross_words_index, emitter, size_px)
        print('</svg>', file=f)
