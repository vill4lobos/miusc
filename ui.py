import curses
import string
import random as rd
from collections import deque
from itertools import islice


def debug():
    curses.nocbreak()
    # self.screen.keypad(0)
    curses.echo()
    curses.endwin()
    breakpoint()


class UI(object):
    GENRE_SEPARATE = 2

    def __init__(self, screen):
        self.screen = screen
        self.y_limit, self.x_limit = screen.getmaxyx()
        self.x_center = self.x_limit // 2
        self.genres_height = 0
        self.albums_height = 2
        self.last_movement = None
        self.y_index = 0
        self.last_axis = ''

        self.dq_album = deque(Get.get_albums())
        self.dq_genre = deque(Get.genre_list)

    """
    Returns a list of tuples with all elements and their lengths that can fit
    at max x.length of terminal with index[0] at the middle of the list
    """
    # TODO: fix list out of range when more than 90 movements in the same
    # direction
    def move_genres_list(self, move=False):

        if move:
            if self.last_movement:
                self.dq_genre.rotate(-1)
            else:
                self.dq_genre.rotate(1)

        count = 0
        i, j = 0, 0
        dq_middle = int(len(self.dq_genre) / 2)

        for i, j in enumerate(range(dq_middle, len(self.dq_genre)), 1):
            count += self.GENRE_SEPARATE * 2

            if (count + len(self.dq_genre[dq_middle - i]) +
               len(self.dq_genre[j])) < self.x_limit:
                count += len(self.dq_genre[dq_middle - i]) + \
                    len(self.dq_genre[j])
            else:
                break

        return deque(islice(self.dq_genre, dq_middle - i, j))

    def move_albums_list(self):
        limit = self.y_limit - self.albums_height - 1

        if self.last_movement:
            if self.y_index == limit:
                self.dq_album.rotate(-1)
            else:
                self.y_index += 1

        elif not self.last_movement:
            if self.y_index == 0:
                self.dq_album.rotate(1)
            elif self.y_index != 0:
                self.y_index -= 1

    def center_str(self, str):
        return self.x_center - (len(str) // 2)

    def display_genres(self, move=False):
        lst_genres = self.move_genres_list(move)

        # TODO: padding around the dq_genres
        len_total = 0  # max(self.x_limit - sum(map(len, lst_genres)), 0) // 2
        for i, item in enumerate(lst_genres):
            if i == len(lst_genres) // 2 + 1:
                self.screen.addstr(0, len_total, item,
                                   curses.A_REVERSE)
            else:
                self.screen.addstr(0, len_total, item,
                                   curses.A_ITALIC)

            len_total += len(item) + 2

    def display_albums(self, move=False):
        if move:
            self.move_albums_list()
        lst_albums = self.dq_album

        for i, item in enumerate(lst_albums):
            if i == self.y_limit - self.albums_height:
                break

            if self.y_index == i:
                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item,
                                   curses.A_BLINK | curses.A_REVERSE)
            else:
                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item, curses.A_BOLD)

    def x_navigate(self, b):
        self.last_axis = 'x'
        self.last_movement = True if b else False
        self.display_ui()

    def y_navigate(self, b):
        self.last_axis = 'y'
        self.last_movement = True if b else False
        self.display_ui()

    def display_ui(self):
        self.screen.refresh()
        self.screen.clear()

        if self.last_axis == 'y':
            self.display_albums(True)
            self.display_genres()

        elif self.last_axis == 'x':
            self.dq_album = deque(Get.get_albums())
            self.y_index = 0
            self.display_albums()
            self.display_genres(True)


class Get:

    genre_list = [str(x) for x in range(1000, 1050)]
    # album_list = [list(string.ascii_lowercase)[rd.randint(0, 26)]
    #               for x in range(0, rd.randint(15, 30))]

    def __init__(self):
        pass

    @staticmethod
    def get_albums():
        return [str(i) + "   " + x for i, x in enumerate(
                [''.join([list(string.ascii_lowercase)[rd.randint(0, 25)]
                 for x in range(0, rd.randint(15, 30))])
                 for x in range(30)])]


def main(screen):

    menu = UI(screen)
    screen.clear()

    menu.display_genres()
    menu.display_albums()

    while True:
        screen.refresh()
        key = screen.getch()

        if key == ord('q'):
            break
        elif key in [curses.KEY_RIGHT, ord('h')]:
            menu.x_navigate(True)
        elif key in [curses.KEY_LEFT, ord('l')]:
            menu.x_navigate(False)
        elif key in [curses.KEY_UP, ord('k')]:
            menu.y_navigate(False)
        elif key in [curses.KEY_DOWN, ord('j')]:
            menu.y_navigate(True)

    screen.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
