import unittest
from karnobh.crosswordist.graphics import (GraphicsEmitter, Rect, Text, EmitterContext, Translate,
                                           SvgGraphicsEmitter)
from io import StringIO


class TextEmitter(GraphicsEmitter):

    def __init__(self):
        super().__init__()
        self.result = []

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, val):
        self._result = []

    def rect(self, x, y, w, h):
        context = self.peek_context()
        vals = [x, y, w, h]
        if context:
            # print(vars(context))
            vals.append(context)
        str_repr = ", ".join(str(v) for v in vals)
        self._result.append(f"rect({str_repr})")

    def text(self, x, y, text, ext=None):
        context = self.peek_context()
        vec = [x, y]
        if context.transform:
            vec = context.transform.apply_vec(vec)
        vals = vec + [f"'{text}'"]
        str_repr = ", ".join(str(v) for v in vals)
        self._result.append(f"text({str_repr})")


class MyTestCase(unittest.TestCase):

    def test_emitter_context_empty(self):
        ctx = EmitterContext()
        self.assertFalse(ctx)

    def test_emitter_context_non_empty(self):
        ctx = EmitterContext(stroke="red")
        self.assertTrue(ctx)
        ctx = EmitterContext(stroke_width=3)
        self.assertTrue(ctx)
        ctx = EmitterContext(transform=Translate(4,3))
        self.assertTrue(ctx)
        ctx = EmitterContext(fill="green")
        self.assertTrue(ctx)

    def test_translate_value_setting(self):
        self.assertRaises(TypeError, lambda: Translate("a",4))
        self.assertRaises(TypeError, lambda: Translate(4, 1 + 3j))
        self.assertEqual(37, Translate(37, 47).x)
        self.assertEqual(47, Translate(37, 47).y)

    def test_translate_vec_apply(self):
        vec = [1, 2, 3]
        t = Translate(10, 10)
        self.assertEqual([11, 12, 3], t.apply_vec(vec))
        # x, y = t.apply_vec((1, 2))
        # print(x, y)
        vec = [5, 6]
        t = Translate(100, 200)
        self.assertEqual([105, 206], t.apply_vec(vec))
        vec = 5, 6
        t = Translate(100, 200)
        self.assertEqual([105, 206], t.apply_vec(vec))
        vec = 5, 6, 7
        t = Translate(100, 200)
        self.assertEqual([105, 206, 7], t.apply_vec(vec))

    def test_text_emitter(self):
        shapes = [
            Rect(10, 10, 30, 30),
            Text(10, 10, "Hello World", context=EmitterContext(
                stroke="blue",
                fill="red",
                stroke_width=2,
                transform=Translate(10, 10)
            )),
            Rect(20, 20, 50, 50)
        ]
        emitter = TextEmitter()
        emitter.push_context(context=EmitterContext(
            stroke=2,
            fill="green",
            transform=None
        ))
        for s in shapes:
            s.emit(emitter)
        # print(emitter.result)
        expected = ['rect(10, 10, 30, 30, EmitterContext(stroke=2, stroke_width=None, '
                    "fill='green', transform=None, mergeable=False))",

                    "text(20, 20, 'Hello World')",

                    'rect(20, 20, 50, 50, EmitterContext(stroke=2, stroke_width=None, '
                    "fill='green', transform=None, mergeable=False))"]
        self.assertEqual(expected, emitter.result)

    def test_svg_emitting(self):
        shapes = [
            Rect(10, 10, 30, 30),
            Text(10, 10, "Hello World", context=EmitterContext(
                # stroke="blue",
                fill="red",
                stroke_width=2,
                transform=Translate(40, 40),
                mergeable=True
            )),
            Rect(20, 20, 50, 50)
        ]

        with StringIO() as f:
            emitter = SvgGraphicsEmitter(f)
            emitter.push_context(context=EmitterContext(
                stroke="purple",
                stroke_width=1,
                fill="green",
                transform=None
            ))
            for s in shapes:
                s.emit(emitter)
            f.seek(0)
            result_lines = [line.rstrip() for line in f]

        expected_lines = [
            "<rect x='10' y='10' width='30' height='30' stroke='purple' stroke_width='1' fill='green' />",
            "<text x='50' y='50' stroke='purple' stroke_width='2' fill='red'>Hello World</text>",
            "<rect x='20' y='20' width='50' height='50' stroke='purple' stroke_width='1' fill='green' />"
        ]

        self.assertEqual(expected_lines, result_lines)