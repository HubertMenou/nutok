import unittest

from nutok.tokens import Shape, Color, Token
from nutok.board import Board
from nutok.board import Vertical, Horizontal


class TestBoardBasic(unittest.TestCase):

    def test_basic(self):
        b = Board(3)
        self.assertEqual(len(b), 0)

    def test_len(self):
        b = Board(3)
        self.assertEqual(len(b), 0)

        tsp = Token(Shape.SQUARE, Color.PURPLE)
        tdp = Token(Shape.DIAMOND, Color.PURPLE)
        tcp = Token(Shape.CIRCLE, Color.PURPLE)

        tsb = Token(Shape.SQUARE, Color.BLUE)
        tdb = Token(Shape.DIAMOND, Color.BLUE)
        tcb = Token(Shape.CIRCLE, Color.BLUE)

        b.add_single_token_no_check(tsp, 0, 0)
        self.assertEqual(len(b), 1)
        b.add_single_token_no_check(tdp, 1, 0)
        self.assertEqual(len(b), 2)
        b.add_single_token_no_check(tcp, 2, 0)
        self.assertEqual(len(b), 3)

        b.add_single_token_no_check(tsb, 0, 1)
        b.add_single_token_no_check(tdb, 1, 1)
        b.add_single_token_no_check(tcb, -1, 1)
        self.assertEqual(len(b), 6)

    def test_widest_line(self):
        b = Board(6)

        tsp = Token(Shape.SQUARE, Color.PURPLE)
        tdp = Token(Shape.DIAMOND, Color.PURPLE)
        tcp = Token(Shape.CIRCLE, Color.PURPLE)

        tsb = Token(Shape.SQUARE, Color.BLUE)
        tdb = Token(Shape.DIAMOND, Color.BLUE)
        tcb = Token(Shape.CIRCLE, Color.BLUE)

        tdy = Token(Shape.DIAMOND, Color.YELLOW)

        b.add_single_token_no_check(tsp, 0, 0)
        b.add_single_token_no_check(tdp, 1, 0)
        b.add_single_token_no_check(tcp, 2, 0)
        b.add_single_token_no_check(tsb, 0, 1)
        b.add_single_token_no_check(tdb, 1, 1)
        b.add_single_token_no_check(tcb, -1, 1)

        line_v = b.get_widest_line(0, 0, Vertical)
        self.assertEqual(line_v[0], tsp)
        self.assertEqual(line_v[1], tdp)
        self.assertEqual(line_v[2], tcp)

        line_h = b.get_widest_line(1, 1, Horizontal)
        self.assertEqual(line_h[0], tdp)
        self.assertEqual(line_h[1], tdb)

        line_plus = b.get_widest_line(1, 2, Horizontal, token=tdy)
        self.assertEqual(line_plus[0], tdp)
        self.assertEqual(line_plus[1], tdb)
        self.assertEqual(line_plus[2], tdy)


if __name__ == '__main__':
    unittest.main()
