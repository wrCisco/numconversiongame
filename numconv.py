#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unix systems only

__author__ = "Francesco Martini"
__version__ = "0.0.1"


import random
import threading
import signal
import argparse
import sys
import os
import time
#import shutil
from functools import wraps
from datetime import datetime
import enum
import pickle


class UserChoices(enum.IntEnum):
    GAME_32_BITS = enum.auto() # starts from 1
    GAME_60_SEC = enum.auto()
    GAME_3_SEC = enum.auto()
    EXIT = enum.auto()

    @classmethod
    def max_value(cls):
        num = ''
        for member in cls:
            if num == '':
                num = member.value
            else:
                num = max((num, member.value))
        return num


if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.realpath(__file__))

HIGH_SCORES = os.path.join(APP_DIR, "highscores.txt")


DEFAULT_HIGH_SCORES = {
    UserChoices.GAME_32_BITS.value: [],
    UserChoices.GAME_60_SEC.value: [],
    UserChoices.GAME_3_SEC.value: []
}

parser = argparse.ArgumentParser()

parser.add_argument(
    '-d',
    '--difficulty',
    choices=('novice', 'intermediate', 'expert', 'n', 'i', 'e'),
    default='intermediate'
)

args = parser.parse_args()

if args.difficulty in ('novice', 'n'):
    secs_for_answer = 14
elif args.difficulty in ('intermediate', 'i'):
    secs_for_answer = 10
else:
    secs_for_answer = 6


# Function not used
def delay(delay=0.):
    """
    Decorator delaying the execution of a function for a while.
    """
    def wrap(f):
        @wraps(f)
        def delayed(*args, **kwargs):
            timer = threading.Timer(delay, f, args=args, kwargs=kwargs)
            timer.start()
        return delayed
    return wrap


def add_high_score(scores:list, user_score:int, pos:int) -> list:
    print("Congratulations! You are in the top ten!")
    name = input("Enter your name: ")
    if len(scores) >= 10:
        try:
            scores.pop(0)
        except IndexError:
            pass
    scores.insert(pos, (name, user_score, datetime.strftime(datetime.now(), "%d-%m-%Y %H.%M")))
    return scores


def save_score(filepath:str, game:int, score:int) -> bool:
    if not os.path.isfile(filepath):
        mode = 'wb'
    else:
        mode = 'r+b'
    with open(filepath, mode) as fh:
        try:
            all_scores = pickle.load(fh)
        except EOFError:
            all_scores = DEFAULT_HIGH_SCORES
            print('using void dict')
        try:
            game_scores = sorted(all_scores[game], key=lambda x: x[1])
        except IndexError:
            game_scores = []
        if len(game_scores) < 10:
            game_scores = add_high_score(game_scores, score, 0)
            # name = input("Enter your name: ")
        else:
            if game_scores[0][1] >= score:
                return False
            for i, hs in enumerate(game_scores):
                if score > hs[1]:
                    continue
                game_scores = add_high_score(game_scores, score, i-1)
                break
        all_scores[game] = sorted(game_scores, key=lambda x: x[1], reverse=True)
        fh.seek(0)
        pickle.dump(all_scores, fh)
    return True


def get_max_lengths(scores:list) -> tuple:
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


def print_score(filepath:str, game:int) -> None:
    with open(filepath, 'rb') as fh:
        try:
            all_scores = pickle.load(fh)
        except EOFError:
            all_scores = DEFAULT_HIGH_SCORES
    try:
        game_scores = sorted(all_scores[game], key=lambda x: x[1], reverse=True)
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



class InputTimedOut(Exception):
    pass


def raise_InputTimedOut(signum, frame):
    raise InputTimedOut


signal.signal(signal.SIGALRM, raise_InputTimedOut)


def bin2hex3secs() -> int:
    score = 0
    errors = 0
    wrong = False
    while True:
        time.sleep(0.1)
        try:
            signal.alarm(3)
            a = bin(random.randint(1, 15))
            pres_a = a[2:].rjust(4, '0')
            print(pres_a)
            b = input("What is the correspondent hex? ")
            signal.alarm(0)
            hexa = hex(int(a, base=2))
            if "{}{}".format("0x" if not str(b).startswith("0x") else "",
                             str(b).casefold().lstrip('0')) == hexa.casefold():
                score += 1
                print("Good!\n")
            else:
                print("Wrong!")
                wrong = True
                raise InputTimedOut
        except InputTimedOut:
            if not wrong:
                print("\nTime's over.")
                signal.alarm(0)
            else:
                wrong = False
            errors += 1
            if errors == 1:
                print("First error.\n")
            elif errors == 2:
                print("Second error.\n")
            elif errors == 3:
                print("Third and last error allowed.\n")
            if errors > 3:
                break
    print("\nGame over. You made {} points!".format(score))
    return score


def bin2hex60secs() -> int:
    score = 0
    try:
        signal.alarm(60)
        while True:
            a = bin(random.randint(1, 15))
            pres_a = a[2:].rjust(4, '0')
            print(pres_a)
            b = input("What is the correspondent hex? ")
            hexa = hex(int(a, base=2))
            if "{}{}".format("0x" if not str(b).startswith("0x") else "",
                             str(b).casefold().lstrip('0')) == hexa.casefold():
                score += 1
                print("Good!\n")
            else:
                print("Wrong!\n")
            time.sleep(0.1)
    except InputTimedOut:
        print("\nTime's over. You made {} points!".format(score))
    return score


def bin2hex() -> int:
    a = bin(random.randint(1, 65535))
    pres_a = a[2:].rjust(16, '0')
    for c in range(len(pres_a), 0, -4):
        pres_a = pres_a[:c]+' '+pres_a[c:]
    print(pres_a)
    try:
        signal.alarm(secs_for_answer)
        b = input("What is the correspondent hex? ")
        signal.alarm(0)
    except InputTimedOut:
        print("\nTime passed, move on.\n")
        return 0
    hexa = hex(int(a, base=2))
    if "{}{}".format("0x" if not str(b).startswith("0x") else "",
                     str(b).casefold().lstrip('0')) == hexa.casefold():
        print("Good!\n")
        return 1
    else:
        print("Booh!\n")
        return 0


def main():
    while True:
        os.system('cls' if sys.platform.startswith('win') else 'clear')
        # print('\n'*shutil.get_terminal_size()[1])
        print("Welcome to the bin2hex challenge!\n"
              "What game do you want to play?\n"
              "({}) 32 bits\n"
              "({}) 60 seconds\n"
              "({}) 3 seconds\n"
              "({}) Exit".format(UserChoices.GAME_32_BITS,
                                 UserChoices.GAME_60_SEC,
                                 UserChoices.GAME_3_SEC,
                                 UserChoices.EXIT))
        choose = input(">>> ")
        # if choose not in (str(x) for x in range(1, UserChoices.max_value() + 1)):
        #    continue
        try:
            choose = int(choose)
            if choose == UserChoices.GAME_32_BITS:
                score = 0
                for x in range(1, 6):
                    score += bin2hex()
                    print("Score: {} on {}.\n".format(score, x))
                    # needed to consume optional user input remained in stdin if the last round was 'TimedOut'
                    # input()
            elif choose == UserChoices.GAME_60_SEC:
                score = bin2hex60secs()
                input("Press enter to continue.\n")
            elif choose == UserChoices.GAME_3_SEC:
                score = bin2hex3secs()
                input("Press enter to continue.\n")
            elif choose == UserChoices.EXIT:
                sys.exit(0)
            else:
                continue
            save_score(HIGH_SCORES, choose, score)
            print_score(HIGH_SCORES, choose)
            input()
        except ValueError:
            pass


if __name__ == '__main__':
    main()