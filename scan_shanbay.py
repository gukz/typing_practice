'''
scan all code, generate the most used word in the code
'''
import os
import re
import json


class IterFile:
    def __init__(self, root, target):
        self.target = target
        self.file_list = self._get_file_list(root)

    def _get_file_list(self, root):
        file_list = []
        for path, dirs, files in os.walk(root):
            for f in files:
                if self.is_target(f):
                    file_list.append('{}/{}'.format(path, f))
            for d in dirs:
                file_list.extend(self._get_file_list('{}/{}'.format(
                    path, d)))
        return file_list

    def is_target(self, files):
        ends = files[files.rfind('.'):]
        return ends in self.target

    def next(self):
        for files in self.file_list:
            file_content = ''
            with open(files, 'r') as f:
                file_content = f.read()
            yield file_content


class WordDict:
    def __init__(self):
        self.word_dict = {}

    def add(self, chars):
        for char in chars:
            char = char.strip()
            if char == '':
                continue
            self.word_dict[char] = self.word_dict.get(char, 0) + 1

    def get_dict(self, topx):
        res = [(n, w) for w, n in self.word_dict.items() if n >= topx]
        res.sort(reverse=True)
        return res

path = '/users/guk/gitstore/shanbay'#news_bee'#'/opt/gukznote'
target = ['.py']
iter_file = IterFile(path, target)
conts = iter(iter_file.next())
word_dict = WordDict()

for cont in conts:
    words = re.split('[\r\n\t\(\)\.\:=\[\],\{\}\+\-\*\/\'\" ]+', cont)
    word_dict.add(words)
res = word_dict.get_dict(50)
last_dict = []
with open('dict.json', 'r') as f:
    last_dict = json.loads(f.read())

with open('dict.json', 'w') as f:
    last_dict.extend([n[1] for n in res])
    f.write(json.dumps(last_dict))


