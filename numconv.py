#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Copyright (c) 2017 Francesco Martini
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__author__ = "Francesco Martini"
__version__ = "0.0.1"
__appname__ = "Numconversiongame"


import sys
import os
import pickle
from datetime import datetime

from games import games
from games.games import Game


debug = True

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

# all name_id must be unique (that's why they're all here)
GAMES = [
    games.Bin2Hex3Secs(name_id='game_3_sec'),
    games.HexSum(name_id='game_hexsum'),
    games.HexMul(name_id='game_hexmul'),
    games.HexDiff(name_id='game_hexdiff'),
    games.HexArithm(name_id='game_arithm'),
    games.Hex2Dec(name_id='game_dec_6_sec'),
    games.Dec2Hex(name_id='game_hex_6_sec'),
    games.RecognizeWord(name_id='recognize_code_point_word')
]

if debug:
    HIGH_SCORES = os.path.join(APP_DIR, "highscores.txt")
else:
    USER_HOME = os.path.expanduser("~")
    if sys.platform.startswith("linux"):
        CONF_PATH = os.path.join(USER_HOME, ".local", "share", __appname__)
    elif sys.platform.startswith("win"):
        try:
            CONF_PATH = os.path.join(os.environ['APPDATA'], __appname__)
        except KeyError:
            CONF_PATH = os.path.join(USER_HOME, "AppData", "Roaming", __appname__)
    elif sys.platform.startswith("darwin"):
        CONF_PATH = os.path.join(USER_HOME, "Library", "Application Support", __appname__)
    else:
        CONF_PATH = os.path.join(USER_HOME, "."+__appname__)
    HIGH_SCORES = os.path.join(CONF_PATH, "highscores.txt")

DEFAULT_HIGH_SCORES = {}
for game_ in GAMES:
    DEFAULT_HIGH_SCORES[game_.name_id] = []


def add_high_score(scores: list, user_score: int, pos: int, level: int) -> list:
    print("Congratulations! You are in the top ten!")
    name = input("Enter your name: ")
    if len(scores) >= 10:
        try:
            scores.pop(0)
        except IndexError:
            pass
    scores.insert(pos,
                  (name,
                   user_score,
                   datetime.strftime(datetime.now(),
                                     "%d-%m-%Y %H.%M"),
                   level))
    return scores


def save_score(filepath: str, game: Game, score: int) -> bool:
    if not os.path.isfile(filepath):
        mode = 'wb'
        if not os.path.isdir(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
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
            game_scores = sorted(all_scores[game.name_id], key=lambda x: x[1])
        except IndexError:
            game_scores = []
        if len(game_scores) < 10:
            game_scores = add_high_score(game_scores, score, 0, game.difficulty)
        else:
            if game_scores[0][1] >= score:
                return False
            for i, hs in enumerate(game_scores):
                if score > hs[1] and i != len(game_scores)-1:
                    continue
                game_scores = add_high_score(game_scores, score, i-1, game.difficulty)
                break
        all_scores[game.name_id] = sorted(game_scores, key=lambda x: x[1], reverse=True)
        fh.seek(0)
        pickle.dump(all_scores, fh)
    return True


def get_max_lengths(scores: list) -> tuple:
    max_len_names = 0
    max_len_scores = 0
    max_len_dates = 0
    max_len_level = 0
    for score in scores:
        if len(score[0]) > max_len_names:
            max_len_names = len(score[0])
        if len(str(score[1])) > max_len_scores:
            max_len_scores = len(str(score[1]))
        if len(score[2]) > max_len_dates:
            max_len_dates = len(score[2])
        # level is not always present
        try:
            if len(score[3]) > max_len_level:
                max_len_level = len(score[3])
        except IndexError:
            pass
    return max_len_names, max_len_scores, max_len_dates, max_len_level


def print_score(filepath: str, game: Game) -> None:
    with open(filepath, 'rb') as fh:
        try:
            all_scores = pickle.load(fh)
        except EOFError:
            all_scores = DEFAULT_HIGH_SCORES
    try:
        game_scores = sorted(all_scores[game.name_id], key=lambda x: x[1], reverse=True)
    except IndexError:
        game_scores = []
    except KeyError:
        print(sys.exc_info(), file=sys.stderr)
        game_scores = []
    len_names, len_scores, len_dates, len_levels = get_max_lengths(game_scores)
    print("Best scores:\n"
          "Nr.  {name:{lnames}}{score:{lscores}}{date:{ldates}}{level:{llevels}}"
          "".format(name="Name",
                    score="Score",
                    date="Date and time",
                    level="Difficulty",
                    lnames=max(len_names, len("Name")) + 2,
                    lscores=max(len_scores, len("Score")) + 2,
                    ldates=max(len_dates, len("Date and time")) + 2,
                    llevels=max(len_levels, len("Difficulty")) + 2)
          )
    if len(game_scores):
        for i, score in enumerate(game_scores):
            # level is not always present
            if len(score) == 4:
                level = score[3]
            else:
                level = ''
            print("{:<5}{name:{lnames}}{score:{lscores}}  {date:{ldates}}{level:{llevels}}"
                  "".format(i+1,
                            name=score[0],
                            score=score[1],
                            date=score[2],
                            level=level,
                            lnames=max(len_names, len("Name")) + 2,
                            lscores=max(len_scores, len("Score")),
                            ldates=max(len_dates, len("Date and time")) + 2,
                            llevels=max(len_levels, len("Difficulty")) +20)
                  )
    else:
        print("No scores have been recorded for this game yet.")
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
                    save_score(HIGH_SCORES, game, score)
                    print_score(HIGH_SCORES, game)
                    input()
                    break
        except ValueError:
            pass


if __name__ == '__main__':
    main()
