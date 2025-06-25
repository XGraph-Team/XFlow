import re

class hstore(dict):
    class parser(object):
        word   = re.compile(r'"([^"]+)"')
        arrow  = re.compile(r'\s*=>\s*')
        comma  = re.compile(r',\s*')

        def __init__(self, text):
            self.position = 0
            self.text     = text

        def __iter__(self):
            while self.peek(self.word):
                key   = self.read(self.word, 1)
                self.read(self.arrow)
                value = self.read(self.word, 1)
                yield key, value
                if self.peek(self.comma):
                    self.read(self.comma)
                else:
                    break

        def read(self, expect, group=0):
            match = expect.match(self.text, self.position)
            if match is None:
                raise Exception('parse error at ' + position)
            self.position = match.end()
            return match.group(group)

        def peek(self, expect):
            return expect.match(self.text, self.position) is not None

    def __init__(self, text):
        super(hstore,self).__init__(self.parser(text))

    def __str__(self):
        return ', '.join('"{0}"=>"{1}"'.format(k,v) for k,v in self.items())

def _main():
    hstore_str = '"foo" => "bar"'
    hstore_dct = hstore(hstore_str)
    assert hstore_dct['foo'] == 'bar'
    assert str(hstore_dct) == '"foo"=>"bar"'
    assert repr(hstore_dct) == "{'foo': 'bar'}"

if __name__ == '__main__':
    _main()
