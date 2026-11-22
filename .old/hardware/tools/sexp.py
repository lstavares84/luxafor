"""Leitor/escritor mínimo de S-expressions do KiCad."""
import re

_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+')


def parse(text):
    stack = [[]]
    for t in _TOK.findall(text):
        if t == "(":
            stack.append([])
        elif t == ")":
            x = stack.pop()
            stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]


def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(y, list) for y in x):
        return "(" + " ".join(x) + ")"
    pad = "\t" * (ind + 1)
    head = [y for y in x if not isinstance(y, list)]
    out = "(" + " ".join(head)
    for y in x:
        if isinstance(y, list):
            out += "\n" + pad + dump(y, ind + 1)
    return out + "\n" + "\t" * ind + ")"


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def unq(s):
    return s[1:-1] if s.startswith('"') else s


def find(x, key):
    return [y for y in x if isinstance(y, list) and y and y[0] == key]


def first(x, key):
    r = find(x, key)
    return r[0] if r else None
