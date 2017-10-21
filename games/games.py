#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import random
import sys
import os
from abc import ABCMeta, abstractmethod
from typing import Callable

import utils
from utils import InputTimedOut


class Game(metaclass=ABCMeta):

    def __init__(self, name: str, repr_name: str, *args, **kwargs) -> None:
        """
        :param name: a string. It's a human readable id,
               and should never change (it's used for saving
               and retrieving high scores).
        :param repr_name: a string. Presentation name (used in main menu).
        :param start_func: function that runs the game inside the game_loop.
               Can optionally accept a dictionary as a parameter with the options
               set in the setup_func, and should return a boolean (True on success,
               False otherwise).
               Should use internally the read_input function from the utils module
               to set the timeout for the user input.
        :param setup_func: function that must return a dictionary with
               settings used in start_func and in game_loop. Options for
               start_func are arbitrary, while game_loop uses
               options with keys 'allowed_errors', 'error_penalty'
               and 'timeout_penalty' whose values must be integers
               (if these options are not present, it uses default values).
        :param description: optional description of the game.
        """
        super().__init__(*args, **kwargs)
        self.name_id = name
        self.repr_name = repr_name
        self.description = ''

    def __str__(self) -> str:
        return self.repr_name

    def __repr__(self) -> str:
        return self.repr_name

    @abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abstractmethod
    def setup(self):
        pass

    def game_loop(self) -> int:
        """
        Standard game setup and main loop.

        :param self: instance of class Game. The game that is played
        :return: score achieved by the player
        """
        if self.description:
            os.system('cls' if os.name == 'nt' else 'clear')
            print("{}\n\nGame description:\n\n{}\n".format(self, self.description))
            input("Press enter when you're ready to begin.\n")
        opts = self.setup()
        max_errors = opts.get('allowed_errors', 3)
        score = 0
        errors = 0
        wrong = False
        while True:
            try:
                if self.run(opts):
                    print("Good!\n")
                    score += 1
                else:
                    print("Wrong!")
                    wrong = True
                    score -= opts.get('error_penalty', 0)
                    raise InputTimedOut
            except InputTimedOut:
                if not wrong:
                    score -= opts.get('timeout_penalty', 0)
                    print("\nTime's passed.")
                else:
                    wrong = False
                errors += 1
                if errors > max_errors:
                    break
                print("Error nr. {}".format(errors), end='')
                if errors == max_errors:
                    print(" and last error allowed.", end='')
                else:
                    print(".", end='')
                input("\nReady to next op?\n")
        print("\nGame over. You made {} points!".format(score))
        input()
        return score


def set_difficulty() -> int:
    user_input = ''
    while user_input not in ('1', '2', '3'):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Set difficulty:\n"
              "(1) Novice\n"
              "(2) Intermediate\n"
              "(3) Expert\n")
        user_input = input(">>> ")
    return int(user_input)


def set_max_value(values: tuple = (15, 127, 255)) -> dict:
    return {'max_value': values[set_difficulty() - 1]}


class Bin2Hex3Secs(Game):

    def __init__(self, *args, **kwargs) -> None:
        self.name_id = 'game_3_sec'
        self.name = 'Bin2hex (3 seconds)'
        self.description = "Convert the binary numbers in their hexadecimal " \
                           "equivalents.\n" \
                           "You'll have three seconds for every number.\n" \
                           "Three errors allowed."
        super().__init__(self.name_id, self.repr_name, *args, **kwargs)

    def run(self, opts: dict) -> int:
        a = random.randint(1, opts['max_value'])
        digits = 0
        a_ = a
        while a_ > 0:
            a_ //= 2
            digits += 1
        digits += 4 - (digits % 4 or 4)
        pres_a = bin(a)[2:].rjust(digits, '0')
        for _ in range(len(pres_a), 0, -4):
            pres_a = pres_a[:_] + ' ' + pres_a[_:]
        print(pres_a)
        b = utils.read_input("What is the correspondent hex? ", 3)
        hex_a = hex(a)
        if "{}{}".format("0x" if not str(b).startswith("0x") else "",
                         str(b).casefold().lstrip('0')) == hex_a.casefold():
            return True
        else:
            return False

    def setup(self) -> dict:
        return set_max_value(values=(15, 255,   65535))


def hexsum(opts: dict) -> bool:
    a = random.randint(0, opts['max_value'])
    b = random.randint(0, opts['max_value'])
    hexa, hexb = hex(a)[2:], hex(b)[2:]
    result = a + b
    hexresult = hex(result).casefold()[2:]
    answer = utils.read_input('{} + {} = '.format(hexa, hexb), 10)
    answer = answer.casefold()
    if answer.startswith('0x'):
        answer = answer[2:]
    if answer != '0'*(len(answer) or 1):
        answer = answer.lstrip('0')
    else:
        answer = '0'
    if answer == hexresult:
        return True
    else:
        return False


def hexmul(opts: dict) -> bool:
    a = random.randint(0, opts['max_value'])
    b = random.randint(0, opts['max_value'])
    hexa, hexb = hex(a)[2:], hex(b)[2:]
    result = a * b
    hexresult = hex(result).casefold()[2:]
    answer = utils.read_input('{} \u00D7 {} = '.format(hexa, hexb), 10)
    answer = answer.casefold()
    if answer.startswith('0x'):
        answer = answer[2:]
    if answer != '0'*(len(answer) or 1):
        answer = answer.lstrip('0')
    else:
        answer = '0'
    if answer == hexresult:
        return True
    else:
        return False


def hexdiff(opts: dict) -> bool:
    a = random.randint(0, opts['max_value'])
    b = random.randint(0, opts['max_value'])
    first, last = max(a, b), min(a, b)
    hex_first, hex_last = hex(first)[2:], hex(last)[2:]
    result = first - last
    hexresult = hex(result).casefold()[2:]
    answer = utils.read_input('{} - {} = '.format(hex_first, hex_last), 10)
    answer = answer.casefold()
    if answer.startswith('0x'):
        answer = answer[2:]
    if answer != '0'*(len(answer) or 1):
        answer = answer.lstrip('0')
    else:
        answer = '0'
    if answer == hexresult:
        return True
    else:
        return False


def hex_random_arithm(opts: dict) -> bool:
    operations = (hexsum, hexmul, hexdiff)
    return operations[random.randint(0, 2)](opts)


def hex2dec(opts: dict) -> bool:
    a = random.randint(1, opts['max_value'])
    repr_a = hex(a)[2:].rjust(2, '0')
    print(repr_a)
    b = utils.read_input("What is the correspondent decimal? ", 6)
    try:
        b = int(b)
    except ValueError:
        raise InputTimedOut
    if b == a:
        return True
    else:
        return False


def dec2hex(opts: dict) -> bool:
    a = random.randint(1, opts['max_value'])
    print(a)
    b = utils.read_input("What is the correspondent hexadecimal? ", 6)
    try:
        b = int(b, base=16)
    except ValueError:
        raise InputTimedOut
    if b == a:
        return True
    else:
        return False


def rec_code_point_word_setup() -> dict:
    try:
        words_set = set()
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                               'words.txt')) as words:
            for word in words: # one word per line
                words_set.add(word.rstrip('\n'))
    except (FileNotFoundError, OSError):
        words_set = {'cosa', 'anno', 'uomo', 'momento', 'modo', 'mondo', 'parola',
                     'mano', 'maggio', 'commissione', 'dito', 'passione',
                     'fenomeno', 'banana', 'computer', 'bicchiere', 'aspirina',
                     'penna', 'canapa', 'scottex', 'mouse', 'cotone', 'finestra',
                     'tavolo', 'rock'}
    seconds = (20, 15, 10)
    time_for_answer = seconds[set_difficulty() - 1]
    options = {'words_set': words_set,
               'time_for_answer': time_for_answer}
    return options


def recognize_code_point_word(opts: dict) -> bool:
    word = random.sample(opts['words_set'], 1)[0]
    print('Code points:')
    for char_ in word:
        try:
            print('{:>02} '.format(hex(ord(char_))[2:]), end='')
        except ValueError:
            print(sys.exc_info())
    print('')
    answer = utils.read_input("Write the word: ", opts['time_for_answer'])
    if word == answer:
        return True
    else:
        return False
