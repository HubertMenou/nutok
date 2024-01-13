from enum import Enum
from typing import List
import random


class Shape(Enum):

    (
        SQUARE,
        DIAMOND,
        CIRCLE,
        SPADE,
        STAR,
        ARROW,
        CROSS,
        KNIGHT
    ) = range(8)


_SHAPES = dict()
_SHAPES[Shape.SQUARE] = dict(char=u'■')
_SHAPES[Shape.DIAMOND] = dict(char=u'◆')
_SHAPES[Shape.CIRCLE] = dict(char=u'●')
_SHAPES[Shape.SPADE] = dict(char=u'♠')
_SHAPES[Shape.STAR] = dict(char=u'🟊')
_SHAPES[Shape.ARROW] = dict(char=u'↕')
_SHAPES[Shape.CROSS] = dict(char=u'⨯')
_SHAPES[Shape.KNIGHT] = dict(char=u'N')


class Color(Enum):

    (
        PURPLE,
        BLUE,
        TURQUOISE,
        GREEN,
        YELLOW,
        ORANGE,
        RED,
        WHITE,
    ) = range(8)


_COLORS = dict()
_COLORS[Color.PURPLE] = dict(char='p', hex='')
_COLORS[Color.BLUE] = dict(char='b', hex='')
_COLORS[Color.TURQUOISE] = dict(char='t', hex='')
_COLORS[Color.GREEN] = dict(char='g', hex='')
_COLORS[Color.YELLOW] = dict(char='y', hex='')
_COLORS[Color.ORANGE] = dict(char='o', hex='')
_COLORS[Color.RED] = dict(char='r', hex='')
_COLORS[Color.WHITE] = dict(char='w', hex='')


class Token:

    def __init__(self, shape: Shape, color: Color):
        """Represents a game token, described by its shape and its color"""
        self.shape = shape
        self.color = color

    def __eq__(self, other):
        return self.shape == other.shape and self.color == other.color

    def __str__(self):
        return f"{_SHAPES[self.shape]['char']}{_COLORS[self.color]['char']}"

    def __repr__(self):
        return str(self)

    def __hash__(self):
        """Enables the use of Token as a dictionary key"""
        return (self.shape, self.color).__hash__()


MAX_TOKEN_ORDER = min(len(Shape), len(Color))


class TokenSet:

    def __init__(self, order: int):
        self.order = order
        self._token_number = order * order
        self._shapes = list(_SHAPES.keys())[:order]
        self._colors = list(_COLORS.keys())[:order]

        self._tokens = dict()
        for p in self._shapes:
            for c in self._colors:
                t = Token(p, c)
                self._tokens[t] = (_SHAPES[p], _COLORS[c])

    def token_number(self):
        return self._token_number

    def all_tokens(self) -> List[Token]:
        return list(self._tokens.keys())

    def __str__(self):
        chars = ",".join([f'({e})' for e in self._tokens.keys()])
        return f"<{chars}>"

    def line_consistency(self, line: List[Token]) -> bool:
        """Checks if a line of tokens is consistent.

        A line is said to be "consistent" iff:
        - it is a line of unique shapes, with always the same color,
        - it is a line of unique colors, with always the same shape.
        Trivial lines are assumed to be consistent (len 0 or 1).
        """
        if len(line) <= 1:
            return True

        if len(line) > self.order:
            return False

        ta, tb = line[0], line[1]

        if ta.shape != tb.shape and ta.color != tb.color:
            return False

        if ta.shape == tb.shape and ta.color == tb.color:
            return False

        if ta.shape == tb.shape:
            # All shapes must be the same
            # All colors must be unique
            tmp_colors = [ta.color, tb.color]
            for k in range(2, len(line)):
                if line[k].shape != ta.shape:
                    return False
                if line[k].color in tmp_colors:
                    return False
                tmp_colors.append(line[k].color)
            return True

        # Here, necessarily: ta.color == tb.color
        # All shapes must be the same
        # All colors must be unique
        tmp_shape = [ta.shape, tb.shape]
        for k in range(2, len(line)):
            if line[k].color != ta.color:
                return False
            if line[k].shape in tmp_shape:
                return False
            tmp_shape.append(line[k].shape)
        return True


class TokenStack:

    def __init__(self, ts: TokenSet):
        """Standard token stack, with 3 times as many
        tokens as in the provided token set"""
        self.stack = ts.all_tokens() + ts.all_tokens() + ts.all_tokens()
        self.shuffle()

    def is_empty(self):
        """Self-explanatory"""
        return len(self.stack) == 0

    def pick(self) -> Token:
        """Returns a token from the stack
        Errors out if the stack is empty."""
        t = self.stack[-1]
        self.stack = self.stack[:-1]
        return t

    def randomly_append(self, t: Token):
        """Appends t at a random place in the stack"""
        if self.is_empty():
            self.stack.append(t)
            return
        idx = random.randint(0, len(self.stack) - 1)
        self.stack.insert(idx, t)

    def shuffle(self):
        """Randomly shuffles the entire stack"""
        random.shuffle(self.stack)
