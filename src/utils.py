import re
import string

class SeekableIterator:
    def __init__(self, iterator):
        self.iterator = iterator
        self.current = None
        self.reuse = False

    def __iter__(self):
        return self
    
    def __next__(self):
        return self.next()

    def next(self):
        if self.reuse:
            self.reuse = False
        else:
            self.current = None
            self.current = next(self.iterator)
        return self.current

    def rewind(self):
        self.reuse = True
