import json

from collections import namedtuple

def config(fname):
    with open(fname, 'r') as file:
        return json.load(file, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
