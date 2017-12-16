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


import operator
import random
import sys
import os
import re
from abc import ABCMeta, abstractmethod

import utils
from utils import InputTimedOut


class Game(metaclass=ABCMeta):

    """
    Abstract base class for games.
    It provides standard setup and structure for console games
    based on a simple loop of questions and answers.

    To create a game, build a subclass that provides name_id and name
    to the parent and overrides the run method (that's the minimum required).
    Optionally, you can override setup and game_loop methods also.
    The standard game_loop method will show a description of the game if
    the subclass defines the attribute self.description.

    name_id:   type str. It's an id used by the program to store and
               retrieving high scores.
    name:      type str. Name used to present the game to the user.

    run:       instance method. It's been called from inside the game_loop
               method and receives a dictionary of options as argument.
               Returns a boolean value to the game_loop.
               Can use internally the read_input function from the utils
               module to set the timeout for the user input.

    setup:     instance method. Returns the dictionary of options that will be
               passed to the run method. The standard implementation provides
               the user with a choice amongst four levels of difficulty
               (novice, intermediate, expert and master), that will set
               the value for the 'max_value' key in the opts dictionary.
               The method set_difficulty, called during the execution of setup,
               also sets the optional attribute self.difficulty (a string) that
               will be used when saving high scores.

    game_loop: instance method. Main game loop.
               First, shows a description of the game if the attribute
               self.description is set.
               Then calls the setup method from which receives a dictionary
               of options. Although the standard setup method fills the
               dictionary with only 'max_value' key, the game_loop looks for
               three other keys, and in their absence they are replaced with
               default values. Those keys are 'allowed_errors' (defaults to 3:
               at the fourth error the game ends), 'error_penalty' (defaults
               to 0: it's a malus on score when the user inserts a wrong
               answer) and 'timeout_penalty' (defaults to 0: same as before
               for timeout).
               After that, begins the real loop, in which the run method is
               called. If the method returns True the score is +1, otherwise
               errors is +1.
               When errors exceeds 'allowed_errors', the game ends and the
               score value is returned as an integer value.

    """
    def __init__(self, name_id: str, name: str, *args, **kwargs) -> None:
        """
        :param name_id: a string. It's a human readable id,
               and should never change (it's used for saving
               and retrieving high scores).
        :param name: a string. Presentation name (used in main menu).
        """
        super().__init__(*args, **kwargs)
        self.name_id = name_id
        self.name = name
        self.difficulty = ''

        # snippet that can be added to self.description in case standard setup method is used.
        self.standard_description = "Three errors allowed.\n\n" \
                                    "Novice: numbers up to F.\nIntermediate: numbers up to 7F.\n" \
                                    "Expert: numbers up to FF.\nMaster: numbers up to FFF.\n"

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    @abstractmethod
    def run(self, opts: dict) -> bool:
        return False

    def setup(self) -> dict:
        return self.set_max_value()

    def set_max_value(self, values: tuple = (15, 127, 255, 4095)) -> dict:
        return {'max_value': values[self.set_difficulty() - 1]}

    def set_difficulty(self, levels: tuple = ('Novice', 'Intermediate',
                                              'Expert', 'Master')) -> int:
        user_input = ''
        prompt = 'Set difficulty:\n'
        for i, level in enumerate(levels, start=1):
            prompt += '({}) {}\n'.format(i, level)
        while user_input not in (str(i) for i in range(1, len(levels)+1)):
            os.system('cls' if os.name == 'nt' else 'clear')
            user_input = input('{}\n>>> '.format(prompt))
        difficulty_level = int(user_input)
        self.difficulty = levels[difficulty_level-1]
        return difficulty_level

    def game_loop(self) -> int:
        """
        Standard game setup and main loop.

        :param self: the game that is played
        :return: score achieved by the player
        """
        os.system('cls' if os.name == 'nt' else 'clear')
        try:  # if self.description is defined, show its content
            print('{}\n\nGame description:\n\n{}\n'.format(self, self.description))
        except AttributeError:
            pass
        input("Press enter when you're ready to begin.\n")
        opts = self.setup()
        max_errors = opts.get('allowed_errors', 3)
        error_penalty = opts.get('error_penalty', 0)
        timeout_penalty = opts.get('timeout_penalty', 0)
        score = 0
        errors = 0
        wrong = False
        while True:
            try:
                if self.run(opts):
                    print('Good!\n')
                    score += 1
                else:
                    print('Wrong!')
                    wrong = True
                    score -= error_penalty
                    raise InputTimedOut
            except InputTimedOut:
                if not wrong:
                    score -= timeout_penalty
                    print("\nTime's passed.")
                else:
                    wrong = False
                errors += 1
                if errors > max_errors:
                    break
                print('Error nr. {}'.format(errors), end='')
                if errors == max_errors:
                    print(' and last error allowed.', end='')
                else:
                    print('.', end='')
                input('\nReady to next op?\n')
        print('\nGame over. You made {} points!'.format(score))
        input()
        return score


class Bin2Hex3Secs(Game):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id  # 'game_3_sec'
        self.name = 'Bin2hex (3 seconds)'
        super().__init__(self.name_id, self.name, *args, **kwargs)
        self.description = "Convert binary numbers to their hexadecimal " \
                           "equivalents.\n" \
                           "You'll have three seconds for every number.\n" \
                           "Three errors allowed."

    def setup(self) -> dict:
        return self.set_max_value(values=(15, 255, 65535))

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
        b = utils.read_input('What is the correspondent hex? ', 3)
        hex_a = hex(a)
        if '{}{}'.format('0x' if not str(b).startswith('0x') else "",
                         str(b).casefold().lstrip('0')) == hex_a.casefold():
            return True
        else:
            return False


class HexArithm(Game):

    def __init__(self, name_id: str, name : str = 'Hex arithmetic',
                 operation: tuple = (), *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = name
        super().__init__(name_id, name, *args, **kwargs)
        self.description = "Calculate the result of the arithmetic operation between " \
                           "two hexadecimal numbers.\n" \
                           "You'll have ten seconds for every operation.\n" + \
                           self.standard_description
        if operation:
            self.operation = operation
        else:
            self.operation = (
                 {'glyph': '+',
                  'operator': operator.add},
                 {'glyph': '-',
                  'operator': operator.sub},
                 {'glyph': '\u00d7',
                  'operator': operator.mul,
                  'difficulty_coefficient': 0x10}
            )

    def setup(self):
        opts = self.set_max_value()
        opts['operation'] = self.operation
        return opts

    def run(self, opts: dict) -> bool:
        a = random.randint(0, opts['max_value'])
        b = random.randint(0, opts['max_value'])

        operator_index = random.randint(0, len(opts['operation'])-1)
        arithmetic_operator = opts['operation'][operator_index]['operator']
        coefficient = opts['operation'][operator_index].get('difficulty_coefficient', 1)
        a //= coefficient
        b //= coefficient

        hexa, hexb = hex(a)[2:], hex(b)[2:]
        result = arithmetic_operator(a, b)
        sign = '-' if result < 0 else ''
        hexresult = sign + hex(abs(result)).lower()[2:]
        answer = utils.read_input('{} {} {} = '.format(
                hexa, opts['operation'][operator_index]['glyph'], hexb), 10)
        answer = answer.lower()
        if re.fullmatch(r'-?(?:0x)?0+', answer):
            # if answer means 0, let be only '0'
            answer = '0'
        else:
            # otherwise strip possible '0x' or starting zeroes while
            # preserving sign
            answer = re.sub(r'^(-?)(?:0x)?0*', r'\1', answer)
        if answer == hexresult:
            return True
        else:
            return False


class HexSum(HexArithm):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Hex sum'
        self.operation = ({'glyph': '+', 'operator': operator.add},)
        super().__init__(self.name_id, self.name, self.operation, *args, **kwargs)
        self.description = "Calculate the sum of the two hexadecimal numbers.\n" \
                           "You'll have ten seconds for every operation.\n" + \
                           self.standard_description


class HexMul(HexArithm):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Hex mul'
        self.operation = ({'glyph': '\u00d7', 'operator': operator.mul},)
        super().__init__(self.name_id, self.name, self.operation, *args, **kwargs)
        self.description = "Calculate the product of the two hexadecimal numbers.\n" \
                           "You'll have ten seconds for every operation.\n" + \
                           self.standard_description


class HexDiff(HexArithm):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Hex diff'
        self.operation = ({'glyph': '-', 'operator': operator.sub},)
        super().__init__(self.name_id, self.name, self.operation, *args, **kwargs)
        self.description = "Calculate the difference of the two hexadecimal numbers.\n" \
                           "You'll have ten seconds for every operation.\n" + \
                           self.standard_description


class Hex2Dec(Game):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Hex2dec'
        super().__init__(self.name_id, self.name, *args, **kwargs)
        self.description = "Convert the hexadecimal numbers to decimal notation.\n" \
                           "You'll have six seconds for every number.\n" + \
                           self.standard_description

    def run(self, opts: dict) -> bool:
        a = random.randint(1, opts['max_value'])
        repr_a = hex(a)[2:].rjust(2, '0')
        print(repr_a)
        b = utils.read_input('What is the correspondent decimal? ', 6)
        try:
            b = int(b)
        except ValueError:
            raise InputTimedOut
        if b == a:
            return True
        else:
            return False


class Dec2Hex(Game):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Dec2hex'
        super().__init__(self.name_id, self.name, *args, **kwargs)
        self.description = "Convert the decimal numbers to hexadecimal notation.\n" \
                           "You'll have six seconds for every number.\n" + \
                           self.standard_description

    def run(self, opts: dict) -> bool:
        a = random.randint(1, opts['max_value'])
        print(a)
        b = utils.read_input('What is the correspondent hexadecimal? ', 6)
        try:
            b = int(b, base=16)
        except ValueError:
            raise InputTimedOut
        if b == a:
            return True
        else:
            return False


class RecognizeWord(Game):

    def __init__(self, name_id: str, *args, **kwargs) -> None:
        self.name_id = name_id
        self.name = 'Recognize code points'
        super().__init__(self.name_id, self.name, *args, **kwargs)
        self.description = "Decode words written as a sequence of hexadecimal numbers " \
                           "to their correspondent sequence of unicode characters.\n" \
                           "Novice: you'll have twenty seconds for every word; " \
                           "intermediate: fifteen seconds; "

    def setup(self) -> dict:
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
        seconds = (20, 15, 10, 5)
        time_for_answer = seconds[self.set_difficulty() - 1]
        options = {'words_set': words_set,
                   'time_for_answer': time_for_answer}
        return options

    def run(self, opts: dict) -> bool:
        word = random.sample(opts['words_set'], 1)[0]
        print('Code points:')
        for char_ in word:
            try:
                print('{:>02} '.format(hex(ord(char_))[2:]), end='')
            except ValueError:
                print(sys.exc_info())
        print('')
        answer = utils.read_input('Write the word: ', opts['time_for_answer'])
        if word == answer:
            return True
        else:
            return False
