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
import enum



class UserChoices(enum.IntEnum):
    GAME_32_BITS = enum.auto()
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


class InputTimedOut(Exception):
    pass


def raise_InputTimedOut(signum, frame):
    raise InputTimedOut


signal.signal(signal.SIGALRM, raise_InputTimedOut)


def bin2hex3secs():
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
                signal.alarm(0)
                break
    print("\nGame over. You made {} points!".format(score))


def bin2hex60secs():
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


def bin2hex():
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
        os.system('cls' if os.name.startswith('win') else 'clear')
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
        if choose not in (str(x) for x in range(1, UserChoices.max_value() + 1)):
            continue
        if int(choose) == UserChoices.GAME_32_BITS:
            score = 0
            for x in range(1, 6):
                score += bin2hex()
                print("Score: {} on {}.\n".format(score, x))
                # needed to consume optional user input remained in stdin if the last round was 'TimedOut'
                input()
        elif int(choose) == UserChoices.GAME_60_SEC:
            bin2hex60secs()
            input("Press enter to continue.\n")
        elif int(choose) == UserChoices.GAME_3_SEC:
            bin2hex3secs()
            input("Press enter to continue.\n")
        elif int(choose) == UserChoices.EXIT:
            sys.exit(0)


if __name__ == '__main__':
    main()