from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from functools import wraps


class Transform(ABC):

    @abstractmethod
    def apply_vec(self, vec): ...


class Translate(Transform):

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

    @staticmethod
    def __check_set_type(val):
        if not isinstance(val, float) and not isinstance(val, int):
            raise TypeError("Set value should be a number")

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self.__check_set_type(val)
        self._x = val

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self.__check_set_type(val)
        self._y = val

    def apply_vec(self, vec):
        vec_x, vec_y, *remaining = vec
        return [vec_x + self.x, vec_y + self.y] + remaining

    def __repr__(self):
        return f"Translate({self.x}, {self.y})"


@dataclass
class EmitterContext:
    stroke: Any | None = None
    stroke_width: float | int | None = None
    fill: Any | None = None
    transform: Transform | None = None
    mergeable: bool = False

    def __bool__(self):
        return any(val for key, val in vars(self).items()
                   if val is not None and key != "mergeable")


class GraphicsEmitter(ABC):

    def __init__(self):
        super().__init__()
        self._context_stack: list[EmitterContext] = []

    @abstractmethod
    def rect(self, x, y, w, h): ...

    @abstractmethod
    def text(self, x, y, text, ext: dict | None = None): ...

    def push_context(self, context: EmitterContext):
        self._context_stack.append(context)

    def pop_context(self):
        return self._context_stack.pop()

    def peek_context(self):
        return self._context_stack[-1] if self._context_stack else None


class SvgGraphicsEmitterError(Exception):
    pass


class SvgGraphicsEmitter(GraphicsEmitter):

    def __init__(self, file):
        super().__init__()
        self.file = file

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, _file):
        if not _file:
            raise SvgGraphicsEmitterError("Passed file parameter doesn't look like a file")
        self._file = _file

    @staticmethod
    def __get_attrs_str(attrs):
        return " ".join(f"{attr.replace('_', '-')}='{attr_val}'" for attr, attr_val in attrs.items()
                        if attr_val is not None and attr != "mergeable")

    def rect(self, x, y, w, h):
        attrs = {
            "x": x, "y": y, "width": w, "height": h,
            **vars(self.peek_context()),
        }
        print(f"<rect {self.__get_attrs_str(attrs)} />", file=self.file)

    def text(self, x, y, text, ext: dict | None = None):
        context = self.peek_context()
        transform = context.transform
        if transform:
            x, y = transform.apply_vec((x, y))
        ext = ext or {}
        attrs = {
            "x": x, "y": y,
            **vars(context),
            **ext
        }
        del attrs['transform']
        print(f"<text {self.__get_attrs_str(attrs)}>{text}</text>", file=self.file)


def with_context(func):
    @wraps(func)
    def _inner(self, emitter, *args, **kwargs):
        if self.context:
            if self.context.mergeable:
                emitter_context_vars = vars(emitter.peek_context())
                self_context_vars = {k: v for k, v in vars(self.context).items()
                                     if v is not None}
                merged_context = {
                    **emitter_context_vars,
                    **self_context_vars
                }
                context = EmitterContext()
                for key, val in merged_context.items():
                    setattr(context, key, val)
            else:
                context = self.context
            emitter.push_context(context)
        result = func(self, emitter, *args, **kwargs)
        if self.context:
            emitter.pop_context()
        return result
    return _inner


class Shape(ABC):

    @abstractmethod
    def emit(self, emitter: GraphicsEmitter): ...


@dataclass
class Rect(Shape):
    x: float
    y: float
    w: float
    h: float
    context: EmitterContext | None = None

    @with_context
    def emit(self, emitter: GraphicsEmitter):
        emitter.rect(self.x, self.y, self.w, self.h)


@dataclass
class Text(Shape):
    x: float
    y: float
    text: str
    text_anchor: str | None = None
    font_size: int | float | None = None
    context: EmitterContext | None = None

    @with_context
    def emit(self, emitter: GraphicsEmitter):
        emitter.text(self.x, self.y, self.text,
                     ext={
                         'text_anchor': self.text_anchor,
                         'font_size': self.font_size,
                     })
