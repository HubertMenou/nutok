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
        self.assertTrue(b.is_empty())

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

    def test_is_empty(self):
        tsp = Token(Shape.SQUARE, Color.PURPLE)
        for k in range(2, len(Shape)):
            b = Board(k)
            self.assertTrue(b.is_empty())
            b.drop_first_token(tsp)
            self.assertFalse(b.is_empty())

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

    def test_drop_first_token(self):
        tsp = Token(Shape.SQUARE, Color.PURPLE)
        b = Board(5)
        self.assertTrue(b.is_empty())
        b.drop_first_token(tsp)
        self.assertFalse(b.is_empty())
        self.assertTrue(b.has_token_at(0, 0))

    def test_single_droppable(self):
        tsp = Token(Shape.SQUARE, Color.PURPLE)
        tdp = Token(Shape.DIAMOND, Color.PURPLE)
        tcp = Token(Shape.CIRCLE, Color.PURPLE)
        tap = Token(Shape.ARROW, Color.PURPLE)
        tkp = Token(Shape.KNIGHT, Color.PURPLE)

        tsb = Token(Shape.SQUARE, Color.BLUE)
        tst = Token(Shape.SQUARE, Color.TURQUOISE)
        tsg = Token(Shape.SQUARE, Color.GREEN)
        tsy = Token(Shape.SQUARE, Color.YELLOW)
        tso = Token(Shape.SQUARE, Color.ORANGE)
        tsr = Token(Shape.SQUARE, Color.RED)
        tsw = Token(Shape.SQUARE, Color.WHITE)

        b = Board(8)
        b.drop_first_token(tsp)

        self.assertTrue(b.single_droppable(tdp, -1, 0))
        self.assertTrue(b.single_droppable(tdp, 0, -1))
        self.assertTrue(b.single_droppable(tdp, 1, 0))
        self.assertTrue(b.single_droppable(tdp, 0, 1))

        self.assertFalse(b.single_droppable(tdp, 1, 1))
        self.assertFalse(b.single_droppable(tdp, 1, -1))
        self.assertFalse(b.single_droppable(tdp, -1, 1))
        self.assertFalse(b.single_droppable(tdp, -1, -1))
        self.assertFalse(b.single_droppable(tdp, 6, 3))

        b.add_single_token(tdp, 0, 1)

        self.assertTrue(b.single_droppable(tcp, 0, 2))
        self.assertTrue(b.single_droppable(tcp, 0, -1))

        b.add_single_token(tcp, 0, 2)

        # Here, b is:
        # ■p  ◆p  ●p

        for t in [tsw, tso, tsy]:
            self.assertTrue(b.single_droppable(t, -1, 0))
            self.assertTrue(b.single_droppable(t, 1, 0))

            self.assertFalse(b.single_droppable(t, 0, -1))

        b.add_single_token(tsw, -1, 0)
        b.add_single_token(tcp, 1, 1)

        # Here, b is:
        #     ●p
        # ■p  ◆p  ●p
        # ■w

        self.assertTrue(b.single_droppable(tdp, 1, 2))
        self.assertTrue(b.single_droppable(tdp, -1, 2))
        self.assertFalse(b.single_droppable(tsg, -1, 1))


if __name__ == '__main__':
    unittest.main()
