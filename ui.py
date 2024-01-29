import curses
import string
import random as rd
from collections import deque
# from functools import reduce


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
        self.positionx = 0
        self.genres_height = 0
        self.albums_height = 2
        self.last_movement = None
        self.y_index = 0
        self.last_axis = ''

        self.dq = deque(Get.get_albums())

    """
    Returns a list of tuples with all elements and their lengths that can fit
    at max x.length of terminal with index[0] at the middle of the list
    """
    # TODO: fix list out of range when more than 90 movements in the same
    # direction
    def create_genres_list(self, lst):
        center = self.center_str(lst[self.positionx])
        left = center
        right = center  # + len(lst[0])
        left_go = self.positionx

        lst_genres = [(center, lst[self.positionx])]

        i, j, stop, b = 0, self.positionx, 0, False
        while i < len(lst) - 1:
            b = not b

            if b:
                right = right + len(lst[j]) + self.GENRE_SEPARATE

                if right >= self.x_limit:
                    break

                lst_genres.append((right, lst[j]))
                stop += len(lst[j]) + self.GENRE_SEPARATE
                j += 1

            else:
                left_go -= 1
                left = left - len(lst[left_go]) - self.GENRE_SEPARATE

                if left <= 0:
                    break

                lst_genres.append((left, lst[left_go]))
                stop += len(lst[left_go]) + self.GENRE_SEPARATE

            if stop >= self.x_limit:
                break

            i += 1

        return lst_genres

    def move_albums_list(self):
        limit = self.y_limit - self.albums_height - 1

        if self.last_movement is True:
            if self.y_index == limit:
                self.dq.rotate(-1)
            else:
                self.y_index += 1

        elif self.last_movement is False:
            if self.y_index == 0:
                self.dq.rotate(1)
            elif self.y_index != 0:
                self.y_index -= 1

    def center_str(self, str):
        return self.x_center - (len(str) // 2)

    def display_genres(self):
        lst_genres = self.create_genres_list(Get.genre_list)
        self.screen.addstr(0, lst_genres[0][0], lst_genres[0][1],
                           curses.A_REVERSE)
        lst_genres.pop(0)

        for i, item in lst_genres:
            self.screen.addstr(0, i, item,
                               curses.A_ITALIC)

    def display_albums(self, move=False):
        if move:
            self.move_albums_list()
        lst_albums = self.dq

        for i, item in enumerate(lst_albums):
            if i == self.y_limit - self.albums_height:
                break

            if self.y_index == i:
                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item,
                                   curses.A_BLINK | curses.A_REVERSE)
                continue

            self.screen.addstr(self.albums_height + i,
                               self.center_str(item), item, curses.A_BOLD)

    def x_navigate(self, b):
        self.last_axis = 'x'
        self.positionx += 1 if b else -1
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

        elif self.last_axis == 'x':
            self.dq = deque(Get.get_albums())
            self.y_index = 0
            self.display_albums()

        self.display_genres()


class Get:

    genre_list = [str(x) for x in range(100, 201)]
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
