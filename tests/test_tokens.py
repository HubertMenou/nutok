import unittest

from nutok.tokens import Shape, Color, Token, TokenSet


class TestToken(unittest.TestCase):

    def test_resources(self):
        """There must be as many colors as pieces"""
        self.assertEqual(len(Shape), len(Color))

    def test_single_token(self):
        """Test the creation of a token"""
        t = Token(Shape.SQUARE, Color.PURPLE)
        self.assertIsNotNone(t)

    def test_token_equality(self):
        """Tests the equal operator on the tokens"""
        ca, cb = Color.PURPLE, Color.BLUE

        for i, pi in enumerate(Shape):
            for j, pj in enumerate(Shape):
                tia, tja = Token(pi, ca), Token(pj, ca)
                tib, tjb = Token(pi, cb), Token(pj, cb)

                if i == j:
                    self.assertEqual(tia, tja)
                    self.assertEqual(tib, tjb)
                else:
                    self.assertNotEqual(tia, tja)
                    self.assertNotEqual(tib, tjb)

                self.assertNotEqual(tia, tjb)
                self.assertNotEqual(tib, tja)

    def test_sizes(self):
        """Tests the number of tokens"""
        for k in range(1, len(Shape) + 1):
            ts = TokenSet(k)
            self.assertEqual(ts.token_number(), k**2)

    def test_consistency(self):
        pass


if __name__ == '__main__':
    unittest.main()
