import curses
import string
import random as rd
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
        self.positiony = 0
        self.old_positiony = 0
        self.genres_height = 0
        self.albums_height = 2

        self.last_lst = Get.album_list

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

    def create_albums_list(self, lst):
        limit = self.y_limit - self.albums_height - 1
        test = self.positiony - self.old_positiony + 1

        if test > limit:
            self.old_positiony = self.positiony

        if self.old_positiony < 0 and self.positiony < 0:
            self.last_lst = lst[self.old_positiony - 1:] + lst[:self.old_positiony]

        elif self.positiony < 0:
            self.last_lst = lst[self.positiony:] + lst[:self.positiony]

        elif self.positiony < self.old_positiony:
            self.last_lst

        elif self.positiony > limit:
            self.old_positiony = self.positiony
            self.last_lst = lst[self.positiony - limit:] + lst[:self.positiony - limit]

        return self.last_lst

    def max_albums(self, lst, max):
        stop = 0

        for i, item in enumerate(lst):
            if i < len(lst) - 1 and             \
               stop + len(lst[i + 1]) >= max:
                return lst[:i + 1]
            else:
                stop += len(item) + self.GENRE_SEPARATE

        return lst

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

    def display_albums(self):
        lst_albums = self.create_albums_list(Get.album_list)
        self.screen.addstr(0, 0, str(self.positiony))
        self.screen.addstr(1, 0, str(self.old_positiony))
        self.screen.addstr(2, 0, str(self.positiony - self.old_positiony + 1))
        self.screen.addstr(3, 0, str(self.y_limit))
        self.screen.addstr(4, 0, str(self.albums_height))
        k = False
        test = self.positiony - self.old_positiony + 1

        for i, item in enumerate(lst_albums):
            if i == self.y_limit - self.albums_height:
                break

            if not k and \
               ((i == self.positiony and (self.positiony >= 0
                        and self.old_positiony >= 0)) or
               (i == ((self.y_limit - self.albums_height) - 
                      (self.old_positiony - self.positiony)) and
                 self.old_positiony > self.positiony > 0) or
                
                (i == test and self.old_positiony < 0) or
                #i == (self.old_positiony + self.old_positiony < 0
                #(i == )
                
               (self.positiony < 0 and i == 0 and test < 0)):

                self.screen.addstr(self.albums_height + i,
                                   self.center_str(item), item,
                                   curses.A_BLINK | curses.A_REVERSE)
                k = True
                continue

            self.screen.addstr(self.albums_height + i,
                               self.center_str(item), item, curses.A_BOLD)

    def navigatex(self, b):
        self.positionx += 1 if b else -1
        self.display_ui()

    def navigatey(self, b):
        if not b and self.positiony < 0 and self.positiony < self.old_positiony:
            self.old_positiony = self.positiony
        #elif b and self.positiony > 0 
        self.positiony += 1 if b else -1
        
        #if self.positiony >= 0:
        #    self.old_positiony = 0
        
        self.display_ui()

    def display_ui(self):
        self.screen.refresh()
        self.screen.clear()
        self.display_genres()
        self.display_albums()


class Get:

    genre_list = [str(x) for x in range(100, 201)]
    #album_list = [list(string.ascii_lowercase)[rd.randint(0, 26)]
    #              for x in range(0, rd.randint(15, 30))]
    album_list = [str(i) + "   " + x for i, x in enumerate(
                  [''.join([list(string.ascii_lowercase)[rd.randint(0, 25)]
                  for x in range(0, rd.randint(15, 30))])
                  for x in range(30)])]

    def __init__(self):
        pass

    def get_albums(self, url):
        pass


def main(screen):

    menu = UI(screen)
    screen.clear()

    menu.display_genres()
    menu.display_albums()

    while True:
        screen.refresh()
        key = screen.getch()

        if key == curses.KEY_ENTER:
            break
        elif key == curses.KEY_RIGHT:
            menu.navigatey(True)
        elif key == curses.KEY_LEFT:
            menu.navigatey(False)
        elif key == curses.KEY_UP:
            menu.navigatey(False)
        elif key == curses.KEY_DOWN:
            menu.navigatey(True)

    screen.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
