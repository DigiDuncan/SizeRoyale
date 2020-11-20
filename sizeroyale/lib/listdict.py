import itertools


class ListDict(dict):
    def getByIndex(self, n):
        return next(itertools.islice(self.values(), n, None))
