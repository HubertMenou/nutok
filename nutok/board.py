from typing import Union, List, Type, Tuple
from nutok.tokens import Shape, Color, Token, TokenSet
from nutok.directions import Direction, Vertical, Horizontal


LOCATION = Tuple[int, int]


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
        """Adds provided token at (i, j). Checks if token is droppable.
        Returns True iff token could be dropped"""
        droppable = self.single_droppable(token, i, j)
        if droppable:
            self.add_single_token_no_check(token, i, j)
        return droppable

    def add_single_token_no_check(self, token: Token, i: int, j: int):
        """Adds a token without checking the games rules"""
        self.dropped[(i, j)] = token

    def drop_first_token(self, token: Token):
        """Drops the first token at (0, 0)"""
        assert self.is_empty()
        self.add_single_token_no_check(token, 0, 0)

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

    def add_multi_token(self, tokens: List[Token], pos_a: LOCATION, pos_b: LOCATION) -> bool:
        """Adds provided tokens along the line defined by
        the locations `pos_a` and `pos_b` (both ends included).
        Checks this line can be dropped.
        Returns True iff all tokens could be dropped"""
        droppable = self.multi_droppable(tokens, pos_a, pos_b)

        if not droppable:
            return False

        locations = self.pos_to_locations(pos_a, pos_b)
        for t, (i, j) in zip(tokens, locations):
            self.add_single_token_no_check(t, i, j)
        return True

    @staticmethod
    def pos_to_locations(pos_a: LOCATION, pos_b: LOCATION) -> (List[LOCATION], Type[Direction]):
        """Given two locations, supposedly on the same axis,
        return the list of locations in between."""
        assert pos_a[0] == pos_b[0] or pos_a[1] == pos_b[1]

        assert pos_a[0] <= pos_b[0] and pos_a[1] <= pos_b[1]

        if pos_a[0] == pos_b[0]:
            locations = [(pos_a[0], k) for k in range(pos_a[1], pos_b[1] + 1)]
            direction = Horizontal
        else:
            locations = [(k, pos_a[1]) for k in range(pos_a[0], pos_b[0] + 1)]
            direction = Vertical

        return locations, direction

    def multi_droppable(self, tokens: List[Token], pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> bool:
        """Checks if the given set of tokens can be dropped on the line
        defined by the locations `pos_a` and `pos_b` (both ends included).

        Assumption
        ----------
        The existing game must already satisfy the game rules.
        """
        locations, direction = self.pos_to_locations(pos_a, pos_b)

        assert len(locations) == len(tokens)

        if len(tokens) == 1:
            return self.single_droppable(
                tokens[0], locations[0][0], locations[0][1])

        # You cannot be consistent and have more token than the order
        if len(tokens) > self.order:
            return False

        # Drop locations must be empty
        for t, (i, j) in zip(tokens, locations):
            if self.has_token_at(i, j):
                return False

        # Perpendicular widest lines must be consistent
        for t, (i, j) in zip(tokens, locations):
            line_t = self.get_widest_line(i, j, direction.perpendicular(), token=t)
            if not self.token_set.line_consistency(line_t):
                return False

        # Line in the main direction must be consistent
        line_dir = self.get_multi_widest_line(tokens, pos_a, pos_b, direction)
        if not self.token_set.line_consistency(line_dir):
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

    def get_multi_widest_line(self, tokens: List[Token], pos_a: LOCATION, pos_b: LOCATION, direction: Type[Direction]):
        """Returns the widest line that can be formed in the provided
        direction, when dropping the tokens in the locations defined by
        the line `pos_a` to `pos_b`.

        Beware, there is no consistency check regarding whether the line
        described by pos_a and pos_b make sense [!]
        """
        i0, j0 = pos_a
        i_prev, j_prev = direction.prev(i0, j0)
        i1, j1 = pos_b
        i_next, j_next = direction.next(i1, j1)

        if self.has_token_at(i_prev, j_prev):
            line_before = self.get_widest_line(i_prev, j_prev, direction)
        else:
            line_before = list()

        if self.has_token_at(i_next, j_next):
            line_after = self.get_widest_line(i_next, j_next, direction)
        else:
            line_after = list()

        line_dir = line_before + tokens + line_after
        return line_dir

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

