from random import randint
import time


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Нельзя стрелять за доску!".center(290)


class UserBoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку".center(290)


class AIBoardUsedException(BoardException):
    def __str__(self):
        time.sleep(1)
        return "противник пытался смухлевать! Ходи заного негодяй!".center(290)


class BoardWrongShipException(BoardException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"{self.x}, {self.y}"


class Ship:
    def __init__(self, nose, l, o):
        self.nose = nose
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.nose.x
            cur_y = self.nose.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        field = f"    -------------------------\n    | 1 | 2 | 3 | 4 | 5 | 6 |\n ----------------------------"
        for i, row in enumerate(self.field):
            field += f"\n| {i + 1} | " + " | ".join(row) + " |\n ----------------------------"

        if self.hid:
            field = field.replace("■", "O")
        return field

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d, player_name):

        if self.out(d):
            raise BoardOutException()

        if d in self.busy and player_name == "User":
            raise UserBoardUsedException()

        if d in self.busy and player_name == "AI":
            raise AIBoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    if player_name == "User":
                        print("Вы уничтожили корабль врага!!!".center(290))

                    elif player_name == "AI":
                        print("О нет, враг уничтожил ваш корабль!!!".center(290))

                    return False

                else:
                    if player_name == "User":
                        print("Так держать, вы подбили корабль врага!!".center(290))

                    elif player_name == "AI":
                        print("Наш корабль попал под обстрел!!".center(290))

                    return True

        self.field[d.x][d.y] = "."
        if player_name == "User":
            print("Вы промахнулись!".center(290))

        elif player_name == "AI":
            print("Враг промазал!".center(290))

        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                player_name = self.__class__.__name__
                repeat = self.enemy.shot(target, player_name)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {d.x + 1} {d.y + 1}".center(290))
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input((" " * 141) + "Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ".center(290))
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ".center(290))
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for l in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def show_boards(self):
        for x, y in zip(str(self.us.board).split('\n'), str(self.ai.board).split('\n')):
            print (f"{x}         |         {y}".center(290))

    def greeting(self):
        print("===================".center(290))
        print("  Добро пожаловать ".center(290))
        print("      в игру       ".center(290))
        print("    морской бой    ".center(290))
        print("===================".center(290))
        print(" формат ввода: x y ".center(290))
        print(" x - номер строки  ".center(290))
        print(" y - номер столбца ".center(290))
        print("===================".center(290))

    def loop(self):
        num = 0
        while True:
            print("\n")
            print("Ваша доска:                                   Вражеская доска:".center(290))
            self.show_boards()
            if num % 2 == 0:
                print("\n")
                print(("=" * 78).center(290))
                print()
                print("Вы ходите!".center(290))
                repeat = self.us.move()
                time.sleep(1)
            else:
                print(("=" * 20).center(290))
                print(("Ходит противник!").center(290))
                time.sleep(1.5)
                print(("противник думает...").center(290))
                time.sleep(2)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print(("=" * 20).center(290))
                print("Последний корабль врага пал! поздравляем, это была блестательная победа".center(290))
                break

            if self.us.board.count == 7:
                print(("=" * 20).center(290))
                print("Вы проиграли, враг уничтожил все ваши корабли!".center(290))
                break
            num += 1
            time.sleep(3)
            print("\n"*100)

    def start(self):
        self.greeting()
        time.sleep(2)
        self.loop()


go = Game()
go.start()