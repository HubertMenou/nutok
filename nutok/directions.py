
class Direction:

    @staticmethod
    def next(i, j):
        raise NotImplemented

    @staticmethod
    def prev(i, j):
        raise NotImplemented


class Vertical(Direction):

    @staticmethod
    def next(i, j):
        return i + 1, j

    @staticmethod
    def prev(i, j):
        return i - 1, j


class Horizontal(Direction):

    @staticmethod
    def next(i, j):
        return i, j + 1

    @staticmethod
    def prev(i, j):
        return i, j - 1
