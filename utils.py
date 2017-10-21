#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import os


class InputTimedOut(Exception):
    pass


if os.name == 'posix':
    import signal

    def raise_InputTimedOut(signum, frame):
        raise InputTimedOut

    signal.signal(signal.SIGALRM, raise_InputTimedOut)
    
elif os.name == 'nt':
    import msvcrt


def win_read_input(prompt: str, timeout: int = 0) -> str:
    """
    Basic input handler with timeout for Windows consoles.
    If timeout == 0, there is no timeout.
    """
    print(prompt, end='', flush=True)
    start_time = time.time()
    user_input = ''
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if ord(char) == 13:  # \r
                break
            elif ord(char) == 8 and user_input:
                user_input = user_input[:len(user_input)-1]
                print(' \b', end='', flush=True)
            elif char.isprintable:
                user_input += char
        if timeout and (time.time() - start_time) > timeout:
            print('')
            raise InputTimedOut
    print('')
    return user_input


def unix_read_input(prompt: str, timeout: int = 0) -> str:
    """
    Basic input handler with timeout for *nix systems' consoles.
    If timeout == 0, there is no timeout.
    """
    signal.alarm(timeout)
    user_input = input(prompt)
    signal.alarm(0)
    return user_input


if sys.platform.startswith('win'):
    read_input = win_read_input
else:
    read_input = unix_read_input
