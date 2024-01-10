import datetime
import os
import time
from typing import Union, List, Type
from nutok.tokens import Shape, Color, Token, TokenSet, TokenStack, MAX_TOKEN_ORDER
from nutok.directions import Direction, Vertical, Horizontal
from nutok.board import Board
import random
from enum import Enum


class Action:
    """
    Supported actions:

    PLAY_TOKEN
    You want to play a token on the board
    Example:    play 2 3 4
        means play token number 2 at position (3, 4), where 3 denotes the row.

    EXCHANGE_TOKEN
    Example:    exchange 2
        means exchange token 2 with one from the stack.

    QUIT
    You don't want to keep playing.

    INVALID
    This is not an action, but rather the error code for a bad action.
    """

    (
        INVALID,
        PLAY_TOKEN,
        EXCHANGE_TOKEN,
        QUIT
    ) = range(4)

    @classmethod
    def parse(cls, msg: str) -> (int, dict):
        items = [e.strip() for e in msg.split(' ')]
        try:
            command = items[0].strip().lower()
            params = items[1:]
            if command.startswith('p'):
                return cls.parse_play(params)
            elif command.startswith('e'):
                return cls.parse_exchange(params)
            elif command.startswith('q'):
                return cls.parse_quit(params)
            else:
                # Non-explicit commands
                if len(items) == 3:
                    return cls.parse_play(items)
                else:
                    raise ValueError(f"command not supported: {command}")
        except IndexError as err:
            return cls.INVALID, dict(reason="invalid index", err=err)
        except ValueError as err:
            return cls.INVALID, dict(reason="invalid data format", err=err)

    @classmethod
    def parse_play(cls, params: List[str]) -> (int, dict):
        if len(params) != 3:
            raise ValueError(f"{len(params)} param(s) provided instead of 3")
        token_index = int(params[0]) - 1
        i = int(params[1])
        j = int(params[2])
        return cls.PLAY_TOKEN, dict(token_index=token_index, i=i, j=j)

    @classmethod
    def parse_exchange(cls, params: List[str]) -> (int, dict):
        if len(params) != 1:
            raise ValueError(f"{len(params)} param(s) provided instead of 1")
        token_index = int(params[0]) - 1
        return cls.EXCHANGE_TOKEN, dict(token_index=token_index)

    @classmethod
    def parse_quit(cls, _) -> (int, dict):
        return cls.QUIT, dict()


def ask_for_order() -> int:
    value = input(f"Number of shapes/colors (2 to {MAX_TOKEN_ORDER}):  ")
    return int(value)


class CliGame:

    def __init__(self, order, nb_players: int):
        self.order = order
        self.b = Board(order)
        self.stack = TokenStack(self.b.token_set)
        self.nb_players = nb_players

        self.players = list()
        for k in range(self.nb_players):
            self.players.append(
                dict(
                    tokens=list(),
                    name=f"Player {k}",
                    score=0
                )
            )

        init_token = self.stack.pick()
        self.b.add_single_token_no_check(init_token, 0, 0)
        for player_id in self.player_ids:
            self.fill_player_stack(player_id)

    @property
    def tokens_per_player(self):
        return self.order

    @property
    def player_ids(self):
        return range(len(self.players))

    def run(self):
        stop = False
        while not stop:
            for k in range(self.nb_players):
                self.print_game()
                stop = self.play_player(k)
                if stop:
                    break
            if self.stack.is_empty():
                print("Stack is now empty, the game ends now.")
                self.quit()

    # Players specific methods
    def get_player_tokens(self, player_id: int):
        return self.players[player_id]['tokens']

    def is_player_stack_empty(self, player_id: int):
        return self.nb_of_tokens_for(player_id) == 0

    def nb_of_tokens_for(self, player_id: int):
        return len(self.get_player_tokens(player_id))

    def add_token_to_player(self, player_id: int, token: Token):
        self.players[player_id]["tokens"].append(token)

    def get_name(self, player_id: int):
        return self.players[player_id]['name']

    def add_score(self, player_id: int, score: int):
        self.players[player_id]["score"] += score
        print(f"{self.get_name(player_id)} won {score} point(s) (total: {self.get_score(player_id)}).")

    def get_score(self, player_id: int) -> int:
        return self.players[player_id]["score"]

    def fill_player_stack(self, player_id: int):
        """Returns True iff it was possible to fully fill the player's stack"""
        while self.nb_of_tokens_for(player_id) < self.tokens_per_player:
            if self.stack.is_empty():
                return False
            token = self.stack.pick()
            self.add_token_to_player(player_id, token)
        return True

    # Game specific actions

    def play_player(self, player_id: int) -> bool:
        if self.is_player_stack_empty(player_id):
            return True

        t_str = ""
        k_str = ""
        available_tokens = self.players[player_id]["tokens"]
        for k, tk in enumerate(available_tokens):
            new_t = str(tk)
            new_k = str(k + 1)
            max_len = max(len(new_t), len(new_k))
            t_str += new_t + (max_len - len(new_t)) * " " + " | "
            k_str += new_k + (max_len - len(new_k)) * " " + " | "

        print(f"=> {self.get_name(player_id)} is playing.")
        print(f"Available tokens: {t_str}")
        print(f"         Indices: {k_str}")

        finish_turn = False
        while not finish_turn:
            action, params = self.ask_player_raw()

            if action == Action.PLAY_TOKEN:
                finish_turn = self.run_action_play(
                    player_id, params['token_index'], params['i'], params['j'])
            elif action == Action.EXCHANGE_TOKEN:
                finish_turn = self.run_action_exchange(
                    player_id, params['token_index'])
            elif action == Action.QUIT:
                self.quit()

    @staticmethod
    def ask_player_raw():
        while True:
            action_str = input("Next move (Play/Exchange/Quit)?")
            action, params = Action.parse(action_str)
            if action == Action.INVALID:
                print(f"Invalid command: {params['reason']}. Please try again!")
                continue
            return action, params

    def run_action_play(self, player_id: int, token_index: int, i: int, j: int) -> bool:
        nb_tokens = len(self.players[player_id]['tokens'])
        if not 0 <= token_index < nb_tokens:
            print("Invalid token position")
            return False
        token = self.players[player_id]['tokens'][token_index]
        droppable = self.b.single_droppable(token, i, j)
        if not droppable:
            print(f"This action is not possible, you can't drop it at ({i}, {j})")
            return False
        del self.players[player_id]['tokens'][token_index]
        could_be_dropped = self.b.add_single_token(token, i, j)
        if not could_be_dropped:
            print("It was impossible to drop the token.")
            return False
        score = self.b.score_count(i, j)
        self.add_score(player_id, score)
        self.fill_player_stack(player_id)
        return True

    def run_action_exchange(self, player_id: int, token_index: int) -> bool:
        nb_tokens = len(self.players[player_id]['tokens'])
        if not 0 <= token_index < nb_tokens:
            print("Invalid token position")
            return False
        if self.stack.is_empty():
            print("Stack is empty, it is useless to exchange your token.")
            return False
        token = self.players[player_id]['tokens'][token_index]
        del self.players[player_id]['tokens'][token_index]
        self.stack.append_and_shuffle(token)
        new_token = self.stack.pick()
        self.add_token_to_player(player_id, new_token)
        return True

    def quit(self):
        self.print_scores()
        self.save_in_history()
        print("See you soon!")
        exit(0)

    def save_in_history(self):
        board = self.b.str_with_indices()
        scores = self.str_scores()
        txt = f"{board}\n\n{scores}"
        file = "game_{}_{}.txt".format(
            self.order,
            datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        file_path = os.path.join('history', file)
        with open(file_path, 'w', encoding='utf8') as writer:
            writer.write(txt)
        print(f"Game saved in {file}")

    # Printing

    def str_scores(self):
        s = "Scores:\n"
        sorted_players = sorted(self.players, key=lambda p: - p['score'])
        for rank, player in enumerate(sorted_players):
            s += f"\t[{rank + 1}] {player['name']}: {player['score']}\n"
        return s[:-1]

    def print_scores(self):
        print(self.str_scores())

    def print_game(self):
        print("----")
        print(self.b.str_with_indices())


def main():
    order = ask_for_order()
    print("Let's play!\n")
    game = CliGame(order, 2)
    game.run()


if __name__ == "__main__":
    main()
