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

        self.dq_album = deque(Get.get_albums())
        self.dq_genre = deque(Get.genre_list)

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
        """Rotate deque if y_index is equal to 0 or limit, otherwise
        increment y_index
        """
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

    # TODO: create center_deque method?
    def center_str(self, str):
        """Center the string in the x axis center"""
        return self.x_center - (len(str) // 2)

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

        # TODO: padding around the dq_genres
        len_total = 0  # max(self.x_limit - sum(map(len, lst_genres)), 0) // 2
        for i, item in enumerate(lst_genres):
            if i == int(len(lst_genres) / 2):
                self.screen.addstr(self.genres_height, len_total, item,
                                   curses.A_REVERSE)
            else:
                self.screen.addstr(self.genres_height, len_total, item,
                                   curses.A_ITALIC)

            len_total += len(item) + 2

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

    def display_ui(self, axis, movement):
        """
        Set movement attributes and display albums based on which axis moved

        axis -- which axis was moved
        movement -- True if down, right and False if up, left
        """
        self.screen.refresh()
        self.screen.clear()

        self.last_movement = True if movement else False

        if axis == 'y':
            self.display_albums(True)
            self.display_genres()

        elif axis == 'x':
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
            menu.display_ui('x', True)
        elif key in [curses.KEY_LEFT, ord('l')]:
            menu.display_ui('x', False)
        elif key in [curses.KEY_UP, ord('k')]:
            menu.display_ui('y', False)
        elif key in [curses.KEY_DOWN, ord('j')]:
            menu.display_ui('y', True)

    screen.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
