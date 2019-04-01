#! /usr/bin/env python3
# File Name: type.py
# Author: gukz
# Created Time: Sun 10 Dec 2017 12:07:23 PM CST
import sys
import time
import json
import select
import termios
from collections import namedtuple


class GUI():
    color = namedtuple(
        'color', ['black', 'red', 'green', 'yellow', 'blue', 'white'])

    def __init__(self):
        self.front_color = self.color(
            black=30, red=31, green=32, yellow=33, blue=34, white=37)
        self.back_color = self.color(
            black=40, red=41, green=42, yellow=43, blue=44, white=47)
        self.bag_color = self.color(
            black=90, red=91, green=92, yellow=93, blue=94, white=97)

    def _print(self, color, text):
        sys.stdout.write('\33[{}m{}\33[0m'.format(color, text))

    def _error_index(self, s1, s2):
        res = 0
        for i in range(min(len(s1), len(s2))):
            if s1[i] == s2[i]:
                res = i + 1
            else:
                break
        return res

    def show(self, word, user_inp, finish, speed):
        sys.stdout.write('\33[2J\33[2A')  # [2J:clc screen, [2A:go back two \n
        sys.stdout.write('\n')
        self._print(
                self.front_color.green,
                f'[{finish} speed: {int(speed)}ms/bit]')
        sys.stdout.write('\n')
        self._print(self.front_color.blue, word)
        sys.stdout.write('\n')
        error_index = self._error_index(word, user_inp)
        self._print(self.front_color.green, user_inp[:error_index])
        self._print(self.front_color.red, user_inp[error_index:])
        self._print(self.front_color.red, '')
        sys.stdout.flush()


class Input():
    def __init__(self):
        fd = sys.stdin.fileno()
        self.old_setting = termios.tcgetattr(fd)
        new_setting = self.old_setting
        new_setting[3] = new_setting[3] & ~termios.ICANON
        new_setting[3] = new_setting[3] & ~termios.ECHONL
        termios.tcsetattr(fd, termios.TCSAFLUSH, new_setting)

    def __del__(self):
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSAFLUSH, self.old_setting)

    def read_char(self):
        r = select.select([sys.stdin], [], [], 0.01)
        rcode = ''
        if len(r[0]) > 0:
            rcode = sys.stdin.read(1)
        return rcode


DICT_FILE_NAME = 'dict.json'
MSG_TEMPLATE = '{}/{}'


def word_type():
    gui = GUI()
    inp = Input()
    speed = 0
    word_dict = json.load(open(DICT_FILE_NAME))
    # skip last stop
    try:
        temp = json.load(open('temp.json'))
    except Exception:
        temp = {DICT_FILE_NAME: 0}
    else:
        temp.setdefault(DICT_FILE_NAME, 0)

    for index, word in enumerate(word_dict):
        if index < temp[DICT_FILE_NAME]:
            continue
        temp[DICT_FILE_NAME] = index
        json.dump(temp, open('temp.json', 'w'))

        t1 = time.time()
        txt = ''
        gui.show(word, txt, MSG_TEMPLATE.format(index, len(word_dict)), speed)
        while True:
            if txt == word:
                speed = 1000*(time.time()-t1)/max(1, len(txt))
                gui.show(
                    word, txt, MSG_TEMPLATE.format(index, len(word_dict)),
                    speed)
                break
            ch = inp.read_char()
            if len(ch) > 0:
                ascii_inp_list = list(bytes(ch.encode('ascii')))
                for ascii_inp in ascii_inp_list:
                    if ascii_inp == 35:
                        break
                    elif ascii_inp == 127:
                        txt = txt[:-1]
                    else:
                        txt += ch
                gui.show(
                    word, txt,
                    MSG_TEMPLATE.format(index, len(word_dict)),
                    speed)
            else:
                pass
                # time.sleep(0.1)


if __name__ == '__main__':
    word_type()
