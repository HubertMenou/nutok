from typing import Union, List, Type, Tuple
from nutok.tokens import Shape, Color, Token, TokenSet
from nutok.directions import Direction, Vertical, Horizontal


class Board:

    TOKEN_SEPARATOR = "  "
    TOKEN_REPLACEMENT = len(str(Token(Shape.SQUARE, Color.PURPLE))) * ' '
    EMPTY_BOARD_TXT = "<EmptyBoard>"

    def __init__(self, order: int):
        """
        Convention
        ----------

        ^ Row position: i
        |
        |
        |
        |
        +--------> Column position: j
        (0, 0)

        :param order: Number of each piece and color
        """
        self.order = order
        self.token_set = TokenSet(order)
        self.dropped = dict()

    def __str__(self):
        """Prints a simple representation of the board"""
        if self.is_empty():
            return self.EMPTY_BOARD_TXT

        r0, r1 = self.min_vert(), self.max_vert()
        c0, c1 = self.min_horiz(), self.max_horiz()

        txt = ""
        for i in range(r0, r1 + 1):
            line = ""
            for j in range(c0, c1 + 1):
                if self.has_token_at(i, j):
                    line += f"{self.get_token(i, j)}"
                else:
                    line += self.TOKEN_REPLACEMENT
                line += self.TOKEN_SEPARATOR
            txt = f"{line}\n{txt}"
        return txt

    def str_with_indices(self):
        """Prints a representation of the board
        with row and column indices on the sides"""

        if self.is_empty():
            return self.EMPTY_BOARD_TXT

        r0, r1 = self.min_vert(), self.max_vert()
        c0, c1 = self.min_horiz(), self.max_horiz()

        txt = ""
        for i in range(r0, r1 + 1):
            line = ""
            for j in range(c0, c1 + 1):
                if self.has_token_at(i, j):
                    line += f"{self.get_token(i, j)}"
                else:
                    line += self.TOKEN_REPLACEMENT
                line += self.TOKEN_SEPARATOR
            txt = f"{line}\n{txt}"

        col_indices = ""
        col_size = len(self.TOKEN_SEPARATOR + self.TOKEN_REPLACEMENT)
        for j in range(c0, c1 + 1):
            col_str = str(j)
            col_indices += col_str + (col_size - len(col_str)) * ' '

        row_size = 3
        row_barrier = "  "
        split_text = txt.splitlines()
        for i in range(len(split_text)):
            idx = r1 - i
            row_str = str(idx)
            split_text[i] = (row_size - len(row_str)) * ' ' + row_str + row_barrier + split_text[i]

        txt = "\n".join(split_text)

        txt = f"{txt}\n{(row_size + len(row_barrier)) * ' ' + col_indices}"

        return txt

    def is_empty(self) -> bool:
        """Says whether a piece has already been dropped"""
        return len(self.dropped) == 0

    def has_at_least_one_neighbor(self, i: int, j: int) -> bool:
        """Says whether the location (i, j) has at least
        one vertical or horizontal neighbor

        Note that this method ignores the content of (i, j)"""
        neighbors = self.get_neighborhood(i, j)
        for p, q in neighbors:
            if self.has_token_at(p, q):
                return True
        return False

    def __len__(self):
        """Returns the number of tokens already dropped"""
        return len(self.dropped)

    def add_single_token(self, token: Token, i: int, j: int) -> bool:
        """Adds provided token at (i, j). Checks if
        Returns True iff piece could be dropped"""
        droppable = self.single_droppable(token, i, j)
        if droppable:
            self.add_single_token_no_check(token, i, j)
        return droppable

    def add_single_token_no_check(self, token: Token, i: int, j: int):
        """Adds a token without checking the games rules"""
        self.dropped[(i, j)] = token

    def single_droppable(self, token: Token, i: int, j: int) -> bool:
        """Checks if provided token can be dropped at (i, j)

        Assumption
        ----------
        The existing game must already satisfy the game rules.
        """
        # You cannot drop above an existing token
        if self.has_token_at(i, j):
            return False

        # You must drop against an existing token
        if not self.has_at_least_one_neighbor(i, j):
            return False

        # The new vertical line must be consistent
        line_v = self.get_widest_line(i, j, Vertical, token=token)
        if not self.token_set.line_consistency(line_v):
            return False

        # The new horizontal line must be consistent
        line_h = self.get_widest_line(i, j, Horizontal, token=token)
        if not self.token_set.line_consistency(line_h):
            return False

        return True

    def score_count(self, i: int, j: int) -> int:
        """Counts the score as if the designated token
        was the last token that got dropped"""
        if not self.has_token_at(i, j):
            return 0

        def line2pts(_line):
            _pts = len(_line)
            if _pts == self.order:
                _pts += self.order
            return _pts

        line_v = self.get_widest_line(i, j, Vertical)
        line_h = self.get_widest_line(i, j, Horizontal)
        return line2pts(line_v) + line2pts(line_h)

    def get_widest_line(self, i, j, direction: Type[Direction], token: Union[None, Token] = None):
        """Returns the widest continuous line of tokens from location (i, j).

        If token is provided, then it puts token at the center of the list.
        If token is None, then it gets the value of the token at (i, j).
        """
        if token is None:
            token = self.get_token(i, j)
        else:
            if self.has_token_at(i, j):
                raise KeyError(f"there is already a token at ({i}, {j})")

        elements = [token]

        i_next, j_next = direction.next(i, j)
        while self.has_token_at(i_next, j_next):
            elements.append(self.get_token(i_next, j_next))
            i_next, j_next = direction.next(i_next, j_next)

        i_prev, j_prev = direction.prev(i, j)
        while self.has_token_at(i_prev, j_prev):
            elements = [self.get_token(i_prev, j_prev)] + elements
            i_prev, j_prev = direction.prev(i_prev, j_prev)

        return elements

    def has_token_at(self, i: int, j: int):
        """Says whether a token has been dropped at location (i, j)"""
        return (i, j) in self.dropped

    def get_token(self, i: int, j: int) -> Token:
        """Returns token at location (i, j) if there is one,
        raises an error otherwise"""
        if not self.has_token_at(i, j):
            raise KeyError(f"no pieces at {(i, j)}")
        return self.dropped[(i, j)]

    def get_raw_token(self, i: int, j: int) -> Union[None, Token]:
        """Returns token at location (i, j) if there is one,
        returns None otherwise"""
        if self.has_token_at(i, j):
            return self.dropped[(i, j)]
        return None

    @staticmethod
    def get_neighborhood(i: int, j: int) -> List[Tuple[int, int]]:
        """Returns the four locations of the horizontal
        and vertical neighbors of (i, j)"""
        return [
            (i - 1, j),
            (i, j - 1),
            (i, j + 1),
            (i + 1, j),
        ]

    def get_all_nearest_empty_locations(self):
        """Returns all the locations near a token that are empty
        Near = "at +/- 1 vertically or +/- 1 horizontally"
        """
        locations = list()

        for i, j in self.dropped.keys():
            for i_n, j_n in self.get_neighborhood(i, j):
                is_empty = not self.has_token_at(i_n, j_n)
                still_unknown = (i_n, j_n) not in locations
                if is_empty and still_unknown:
                    locations.append((i_n, j_n))

        return locations

    def _furthest_component(self, min_or_max, axis: int):
        if self.is_empty():
            return None
        return min_or_max([e[axis] for e in self.dropped.keys()])

    def max_vert(self):
        return self._furthest_component(max, 0)

    def min_vert(self):
        return self._furthest_component(min, 0)

    def max_horiz(self):
        return self._furthest_component(max, 1)

    def min_horiz(self):
        return self._furthest_component(min, 1)

