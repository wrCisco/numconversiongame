#!/usr/bin/env python3
# -*- coding: utf-8 -*-


__author__ = "Francesco Martini"
__version__ = "0.0.1"


import sys
import os
import pickle
from datetime import datetime

from .games import games
from .games.games import Game


GAMES = [
    Game(
        name='game_3_sec',
        repr_name='Bin2hex (3 seconds)',
        start_func=games.bin2hex3secs,
        setup_func=lambda: games.set_max_value((15, 255, 65535)),
        description="Convert the binary numbers in their hexadecimal "
                    "equivalents.\n"
                    "You'll have three seconds for every number.\n"
                    "Three errors allowed."
    ),
    Game(
        name='game_hexsum',
        repr_name='Hex sum',
        start_func=games.hexsum,
        setup_func=games.set_max_value
    ),
    Game(
        name='game_hexmul',
        repr_name='Hex mul',
        start_func=games.hexmul,
        setup_func=games.set_max_value
    ),
    Game(
        name='game_hexdiff',
        repr_name='Hex diff',
        start_func=games.hexdiff,
        setup_func=games.set_max_value
    ),
    Game(
        name='game_arithm',
        repr_name='Hex arithmetic',
        start_func=games.hex_random_arithm,
        setup_func=games.set_max_value
    ),
    Game(
        name='game_dec_6_sec',
        repr_name='Hex2dec (6 seconds)',
        start_func=games.hex2dec,
        setup_func=games.set_max_value
    ),
    Game(
        name='game_hex_6_sec',
        repr_name='Dec2hex (6 seconds)',
        start_func=games.dec2hex,
        setup_func=games.set_max_value
    ),
    Game(
        name='recognize_code_point_word',
        repr_name='Recognize code points',
        start_func=games.recognize_code_point_word,
        setup_func=games.rec_code_point_word_setup
    )
]

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

HIGH_SCORES = os.path.join(APP_DIR, "highscores.txt")

DEFAULT_HIGH_SCORES = {}
for game_ in GAMES:
    DEFAULT_HIGH_SCORES[game_.name] = []


def add_high_score(scores: list, user_score: int, pos: int) -> list:
    print("Congratulations! You are in the top ten!")
    name = input("Enter your name: ")
    if len(scores) >= 10:
        try:
            scores.pop(0)
        except IndexError:
            pass
    scores.insert(pos, (name, user_score, datetime.strftime(datetime.now(),
                                                            "%d-%m-%Y %H.%M")))
    return scores


def save_score(filepath: str, game: str, score: int) -> bool:
    if not os.path.isfile(filepath):
        mode = 'wb'
    else:
        mode = 'r+b'
    with open(filepath, mode) as fh:
        try:
            all_scores = pickle.load(fh)
            for k, v in DEFAULT_HIGH_SCORES.items():
                try:
                    all_scores[k]
                except KeyError:
                    all_scores[k] = v
        except EOFError:
            all_scores = DEFAULT_HIGH_SCORES
            print('using void dict')
        try:
            game_scores = sorted(all_scores[game], key=lambda x: x[1])
        except IndexError:
            game_scores = []
        if len(game_scores) < 10:
            game_scores = add_high_score(game_scores, score, 0)
        else:
            if game_scores[0][1] >= score:
                return False
            for i, hs in enumerate(game_scores):
                if score > hs[1] and i != len(game_scores)-1:
                    continue
                game_scores = add_high_score(game_scores, score, i-1)
                break
        all_scores[game] = sorted(game_scores, key=lambda x: x[1], reverse=True)
        fh.seek(0)
        pickle.dump(all_scores, fh)
    return True


def get_max_lengths(scores: list) -> tuple:
    max_len_names = 0
    max_len_scores = 0
    max_len_dates = 0
    for n, s, d in scores:
        if len(n) > max_len_names:
            max_len_names = len(n)
        if len(str(s)) > max_len_scores:
            max_len_scores = len(str(s))
        if len(d) > max_len_dates:
            max_len_dates = len(d)
    return max_len_names, max_len_scores, max_len_dates


def print_score(filepath: str, game: Game) -> None:
    with open(filepath, 'rb') as fh:
        try:
            all_scores = pickle.load(fh)
        except EOFError:
            all_scores = DEFAULT_HIGH_SCORES
    try:
        game_scores = sorted(all_scores[game.name], key=lambda x: x[1], reverse=True)
    except IndexError:
        game_scores = []
    len_names, len_scores, len_dates = get_max_lengths(game_scores)
    print("Migliori punteggi:\n"
          "Nr.  {name:{lnames}}{score:{lscores}}{date:{ldates}}"
          "".format(name="Nome",
                    score="Punteggio",
                    date="Data e ora",
                    lnames=max(len_names, len("Nome")) + 2,
                    lscores=max(len_scores, len("Punteggio")) + 2,
                    ldates=max(len_dates, len("Data e ora")) + 2))
    if len(game_scores):
        for i, (name, score, date) in enumerate(game_scores):
            print("{:<5}{name:{lnames}}{score:{lscores}}  {date:{ldates}}"
                  "".format(i+1,
                            name=name,
                            score=score,
                            date=date,
                            lnames=max(len_names, len("Nome")) + 2,
                            lscores=max(len_scores, len("Punteggio")),
                            ldates=max(len_dates, len("Data e ora")) + 2))
    else:
        print("Nessun punteggio è stato ancora registrato per questo gioco.")
    print("")


def main():
    while True:
        os.system('cls' if sys.platform.startswith('win') else 'clear')
        print("Welcome to the bin2hex challenge!\n"
              "What game do you want to play?")
        for i, game in enumerate(GAMES, 1):
            print("({}) {}".format(i, game))
        print("({}) Exit".format(len(GAMES)+1))
        choose = input(">>> ")
        try:
            choose = int(choose)
            if choose == len(GAMES) + 1:
                sys.exit(0)
            for game in GAMES:
                if choose == GAMES.index(game) + 1:
                    score = game.game_loop()
                    save_score(HIGH_SCORES, game.name, score)
                    print_score(HIGH_SCORES, game)
                    input()
                    break
        except ValueError:
            pass


if __name__ == '__main__':
    main()
