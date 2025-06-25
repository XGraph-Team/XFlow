import re

# syntax of poly files;
# name
# number
# indented list of longitude, latitude
# end
# possibly another number
# another end

class PolyfileParser(object):
    newline     = re.compile(r'\s*\n')
    whitespace  = re.compile(r'\s+')
    end         = re.compile(r'END')
    word        = re.compile(r'\w+')
    number      = re.compile(r'-?\d\.\d+E[+-]\d+')
    identifier  = re.compile(r'!?\d+')

    class Error(Exception):
        pass

    def parse(self, buf):
        self.buf = buf
        self.position = 0
        name     = self.read(self.word)
        sections = {}
        self.read(self.newline)
        while not self.peek(self.end):
            # read section
            identifier = self.read(self.identifier)
            sequence   = []
            self.read(self.newline)
            while not self.peek(self.end):
                # read sequence
                self.read(self.whitespace)
                longitude = float(self.read(self.number))
                self.read(self.whitespace)
                latitude = float(self.read(self.number))
                coordinates = (longitude, latitude)
                sequence.append(coordinates)
                self.read(self.newline)
            self.read(self.end)
            self.read(self.newline)
            sections[identifier] = sequence
        self.read(self.end)
        if self.peek(self.newline):
            self.read(self.newline)
        return name, sections

    def peek(self, expect):
        return expect.match(self.buf, self.position) is not None

    def read(self, expect):
        match = expect.match(self.buf, self.position)
        if match is None:
            raise self.Error("%s was not matched (got %s...)" % (expect.pattern, self.buf[self.position:self.position+10]))
        self.position = match.end()
        return match.group()
