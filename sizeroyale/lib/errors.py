class ParseError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


class GametimeError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
