from typing import Union, List, Type
from nutok.tokens import Shape, Color, Token, TokenSet, TokenStack
from nutok.directions import Direction, Vertical, Horizontal
from nutok.board import Board
import random


def demo():
    order = 6

    attempt = 0
    maxi = 0
    while True:
        attempt += 1
        count, board = try_a_game(order=order, verbose=False, pick_attempts=30)
        if count > maxi:
            maxi = count
            print(board)
            print(f"^ Best so far with {count} in a row (currently in {attempt})")
        if count > 30:
            print(board)
            print(f"Got there in {attempt} attempts.")
            print(f"Could play {count} times in a row. {3 * order * order - count} left.")
            break


def try_a_game(order=6, pick_attempts=20, verbose=False):

    b = Board(order)
    stack = TokenStack(b.token_set)

    t0 = stack.pick()
    b.add_single_token_no_check(t0, 0, 0)

    count = 0
    while not stack.is_empty():
        count += 1

        t = stack.pick()
        okay = False

        for _ in range(pick_attempts):
            empty_loc = b.get_all_nearest_empty_locations()
            eval_drop = [(i, j, b.single_droppable(t, i, j)) for i, j in empty_loc]
            droppable = [e for e in eval_drop if e[2]]

            if len(droppable) == 0:
                stack.randomly_append(t)
                t = stack.pick()
            else:
                okay = True
                break

        if not okay:
            if verbose:
                print("Could not pick a proper piece")
            break

        random.shuffle(droppable)
        ik, jk, _ = droppable[0]
        b.add_single_token(t, ik, jk)
        if verbose:
            print(f"=>No:{count}, ({t},{ik},{jk})" + 30 * "-")
            print(b)

    return count, b


if __name__ == "__main__":
    demo()
