class OutputException(Exception):
    def __init__(self, outputValue):
        self.outputValue = outputValue

class EndloopException(Exception):
    pass

class SkiploopException(Exception):
    pass

class LexerException(Exception):
    pass

class ParserException(Exception):
    pass

class QueryException(Exception):
    pass