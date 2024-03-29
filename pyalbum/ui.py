import curses
from collections import deque
from itertools import islice
import requests
from database import Get as GetDB

from urllib3.exceptions import HTTPError
from requests.exceptions import ConnectionError


def debug():
    curses.nocbreak()
    # self.screen.keypad(0)
    curses.echo()
    curses.endwin()
    breakpoint()


class UI(object):
    """
    Used to interact and manage the UI elements of the curses library

    Attr:
    y_limit, x_limit : int
        the limits of the terminal in each axis
    x_center : int
        the center position of the x axis of the terminal in session
    genres_height : int
        position where genres will be written over the x axis
    albums_height : int
        position where albums will start being written over the y axis
    last_movement : bool
        True if last movement was down or right, and False if left or up
    y_index : int
        current position of the album displayed in screen, never going
        below 0, or above x_limit
    """
    GENRE_SEPARATE = 2

    def __init__(self, screen):
        self.screen = screen
        self.y_limit, self.x_limit = screen.getmaxyx()
        self.x_center = self.x_limit // 2
        self.genres_height = 0
        self.albums_height = 2
        self.last_movement = None
        self.y_index = 0
        self.current_genre = ''

        self.dq_genre = deque(Get.get_genres())
        self.dq_album = deque()

    def move_genres_list(self, move=False):
        """
        Return a deque with less numbers of elements than x_limit

        Get the middle index of the deque, and looking ahead and behind it,
        get the length of the maximum range of elements, (i, j), that can
        fit inside x_limit. Then return a isliced deque with odd number of
        elements

        move -- True if x axis movement was executed
        """
        if move:
            if self.last_movement:
                self.dq_genre.rotate(-1)
            else:
                self.dq_genre.rotate(1)

        count = 0
        i, j = 0, 0
        dq_middle = self.center_lst(self.dq_genre)
        self.current_genre = self.dq_genre[dq_middle]

        for i, j in enumerate(range(dq_middle, len(self.dq_genre) - i), 1):
            count += self.GENRE_SEPARATE * 2

            if (count + len(self.dq_genre[dq_middle - i]) +
               len(self.dq_genre[j])) < self.x_limit:

                count += len(self.dq_genre[dq_middle - i]) + \
                    len(self.dq_genre[j])
            else:
                break

        # TODO: makes any difference which genre comes first?
        if dq_middle - i < 0:
            return self.dq_genre

        dq = deque(islice(self.dq_genre, dq_middle - i, j))
        self.current_genre = dq[self.center_lst(dq)]
        return dq

    def move_albums_list(self):
        """
        Rotate deque if y_index is equal to 0 or limit, otherwise
        increment y_index
        """

        limit = 0
        if len(self.dq_album) - 1 > self.y_index:
            limit = self.y_limit - self.albums_height - 1
        else:
            limit = len(self.dq_album) - 1

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

    def change_albums_list(self):
        self.dq_album = deque(Get.genres_dct[self.current_genre])

    def center_lst(self, lst):
        """Return the middle index of some indexable object"""
        return len(lst) // 2

    def center_str(self, str):
        """Center the string in the x axis center"""
        return self.x_center - (len(str) // 2)

    def cut_str(self, str):
        """Cut string if content greater than x_limit"""
        return str[:self.x_limit - 2]

    def assert_string_size(self, lst):
        """Change the size of the contents of a list of strings"""
        for i, item in enumerate(lst):
            if len(item) >= self.x_limit:
                lst[i] = self.cut_str(item)
        return lst

    def display_genres(self, move=False):
        """
        Write the elements of lst_genres on the screen

        Write the elements of lst_genres on the screen height = genres_height,
        and as lst_genres has an odd number of elements, write the middle one
        differently

        move --True if the last user movement was on the x axis, to rotate
        the deque in move_genres_list(), otherwise just generate the list
        """

        lst_genres = self.move_genres_list(move)

        len_total = max(self.x_limit - (sum(map(len, lst_genres)) +
                                        ((len(lst_genres) - 1) *
                                         self.GENRE_SEPARATE)),
                        0) // 2

        for i, item in enumerate(lst_genres):
            if i == self.center_lst(lst_genres):
                self.screen.addstr(self.genres_height, len_total, item,
                                   curses.A_REVERSE)
            else:
                self.screen.addstr(self.genres_height, len_total, item,
                                   curses.A_ITALIC)

            len_total += len(item) + self.GENRE_SEPARATE

    def display_albums(self, move=False):
        """
        Write the elements of lst_albums along the y axis

        Write the elements of lst_albums along the y axis starting from
        albums_height, and making the index == y_index one blinking

        move -- True if the last user movement was on the y axis, otherwise
        it will change the list of albums being presented
        """
        if move:
            self.move_albums_list()

        self.assert_string_size(self.dq_album)

        for i, item in enumerate(self.dq_album):
            if i == self.y_limit - self.albums_height:
                break

            if self.y_index == i:
                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item,
                                   curses.A_BLINK | curses.A_REVERSE)
            else:
                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item, curses.A_BOLD)

    def display_ui(self, axis='', movement=None):
        """
        Set movement attributes and display albums based on which axis moved

        axis -- which axis was moved
        movement -- True if down, right and False if up, left
        """
        self.screen.refresh()
        self.screen.clear()

        if movement is not None:
            self.last_movement = True if movement else False

        self.display_genres(True if axis == 'x' else False)

        if axis in ['x', '']:
            self.change_albums_list()
            self.y_index = 0

        self.display_albums(True if axis == 'y' else False)


class Get:

    genres_dct = {}
    # album_list = [list(string.ascii_lowercase)[rd.randint(0, 26)]
    #               for x in range(0, rd.randint(15, 30))]

    def __init__(self):
        pass

    # @staticmethod
    # def get_albums(genre):
    #     return Get.genres_dct[]

    @staticmethod
    def get_genres():

        try:
            r = requests.get("http://127.0.0.1:5000/all").json()
        except (ConnectionError, HTTPError) as e:
            _ = e  # TODO: create logging
            db = GetDB()
            r = db.get_all_albums()

        for genre in r:
            Get.genres_dct.update(genre)
        return Get.genres_dct.keys()


def main(screen):

    menu = UI(screen)
    screen.clear()

    menu.display_ui()
    while True:
        screen.refresh()
        key = screen.getch()

        if key == ord('q'):
            break
        elif key in [curses.KEY_RIGHT, ord('h')]:
            menu.display_ui('x', True)
        elif key in [curses.KEY_LEFT, ord('l')]:
            menu.display_ui('x', False)
        elif key in [curses.KEY_UP, ord('k')]:
            menu.display_ui('y', False)
        elif key in [curses.KEY_DOWN, ord('j')]:
            menu.display_ui('y', True)

    screen.refresh()
