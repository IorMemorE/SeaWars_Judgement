class Boat:
    __slots__ = ["kind", "x", "y", "isv", "left"]
    """
    isv: orientation is vert
    """

    def __init__(self, kind: int, x: int, y: int, isv: bool) -> None:
        assert 1 <= kind <= 4
        assert 1 <= x <= 10
        assert 1 <= y <= 10
        if isv:
            assert 1 <= x + kind <= 11
        else:
            assert 1 <= y + kind <= 11
        assert type(isv) == bool
        self.kind = kind
        self.left = kind
        self.x = x
        self.y = y
        self.isv = isv


def board_set[T](board: list[list[T]], boat: Boat, value: T):
    if boat.isv:
        for row in range(boat.x - 1, boat.x + boat.kind + 1):
            board[row][boat.y - 1] = value
            board[row][boat.y] = value
            board[row][boat.y + 1] = value
    else:
        for col in range(boat.y - 1, boat.y + boat.kind + 1):
            board[boat.x - 1][col] = value
            board[boat.x][col] = value
            board[boat.x + 1][col] = value


class BArray:
    __slots__ = ["arr"]

    def __init__(self, bf) -> None:  # type: ignore
        self.arr: list[Boat] = bf.arr


class BoatsBuffer:
    __slots__ = ["arr", "cnts", "cboard"]

    def __init__(self) -> None:
        self.arr: list[Boat] = []
        self.cnts = [0, 4, 3, 2, 1]
        self.cboard = [[False] * 12 for i in range(12)]

    def is_occupied(self, boat: Boat) -> bool:
        if boat.isv:
            for row in range(boat.x, boat.x + boat.kind):
                if self.cboard[row][boat.y]:
                    return True
        else:
            for col in range(boat.y, boat.y + boat.kind):
                if self.cboard[boat.x][col]:
                    return True
        return False

    def mset(self, boat: Boat, value: bool):
        board_set(self.cboard, boat, value)

    def add_boat(self, boat: Boat):
        assert self.cnts[boat.kind] > 0
        assert not self.is_occupied(boat)
        self.cnts[boat.kind] -= 1
        self.arr.append(boat)
        self.mset(boat, True)

    def remove_boat(self, id: int = -1):
        if id == -1:
            id = len(self.arr) - 1
        b = self.arr[id]
        self.mset(b, False)
        self.arr.remove(self.arr[id])
        for a in self.arr:
            self.mset(a, True)

    def assume(self) -> BArray:
        assert self.cnts == [0, 0, 0, 0, 0]
        assert len(self.arr) == 10
        return BArray(self)


class SeaWar:
    __slots__ = ["mboard", "boats", "belong", "oboard", "hp", "ohit"]

    def __init__(self, boats: BArray) -> None:
        # my board
        self.mboard = [[False] * 12 for _ in range(12)]
        # other's board
        self.oboard = [[False] * 12 for _ in range(12)]
        self.ohit = [[False] * 12 for _ in range(12)]
        # boats
        self.boats = boats.arr
        # belong
        self.belong = [[-1] * 12 for _ in range(12)]
        for i in range(len(self.boats)):
            b = self.boats[i]
            if b.isv:
                for row in range(b.x, b.x + b.kind):
                    self.belong[row][b.y] = i
            else:
                for col in range(b.y, b.y + b.kind):
                    self.belong[b.x][col] = i
        self.hp = 10

    def as_data(self) -> str:
        rep = 0
        for row in self.mboard[1:11]:
            for it in row[1:11]:
                rep *= 2
                rep += 1 if it else 0
        return f"{rep:25x}"

    def update_from(self, s: str):
        assert len(s) == 25
        rep = int(s, base=16)
        for row_id in range(10, 0, -1):
            for it_id in range(10, 0, -1):
                self.oboard[row_id][it_id] = bool(rep % 2 != 0)
                rep //= 2

    def success_hit(self, x: int, y: int):
        self.ohit[x][y] = True

    def has_filled(self, x: int, y: int) -> bool:
        return self.mboard[x][y]

    def try_attack(self, x: int, y: int) -> bool:
        if self.has_filled(x, y):
            raise
        self.mboard[x][y] = True
        tar = self.belong[x][y]
        if tar == -1:
            return False
        tar = self.boats[tar]
        tar.left -= 1
        if tar.left == 0:
            board_set(self.mboard, tar, True)
            self.hp -= 1
        return True

    def alive(self) -> bool:
        return self.hp != 0


def standard_palce() -> BoatsBuffer:
    a = BoatsBuffer()
    a.add_boat(Boat(1, 1, 1, False))
    a.add_boat(Boat(2, 3, 1, False))
    a.add_boat(Boat(2, 5, 1, False))
    a.add_boat(Boat(1, 7, 1, False))
    a.add_boat(Boat(2, 9, 1, True))
    a.add_boat(Boat(1, 1, 3, False))
    a.add_boat(Boat(1, 1, 5, False))
    a.add_boat(Boat(3, 1, 7, False))
    a.add_boat(Boat(3, 3, 4, True))
    a.add_boat(Boat(4, 3, 6, True))
    return a
