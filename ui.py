import curses
#from functools import reduce


def debug():
    curses.nocbreak()
    #self.screen.keypad(0)
    curses.echo()
    curses.endwin()
    breakpoint()


class UI(object):
    GENRE_SEPARATE = 2

    def __init__(self, screen):
        self.screen = screen
        self.y_limit, self.x_limit = screen.getmaxyx()
        self.x_center = self.x_limit // 2

    def generate_genres(self):
        old_lst = self.max_genres(Get.genre_list, self.x_limit)
        lst = [(len(old_lst[0]), old_lst[0])]

        for i in range(1, len(old_lst) - 1):
            lst.append((len(old_lst[i]) + lst[i - 1][0] + self.GENRE_SEPARATE,
                       old_lst[i]))

        return lst

    """
    Returns a list with all elements that can fit at max x.length of terminal
    with index[0] at the middle of the list
    """
    def max_genres(self, lst, max):
        stop = 0
        index = 0

        for i, item in enumerate(lst):
            if i < len(lst) - 1 and             \
                stop + len(lst[i + 1]) + self.GENRE_SEPARATE >= max:
                # return lst[:i + 1]
                index = i
                break
            else:
                stop += len(item) + self.GENRE_SEPARATE

        #return map(lambda x: (len(x) + self.GENRE_SEPARATE, x),
        return lst[-index // 2:] + lst[:index // 2]

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
        lst_genres = self.generate_genres()

        for i, item in lst_genres:
            self.screen.addstr(0, i, item,
                               curses.A_ITALIC)

    def display_albums(self):
        max = self.max_albums(Get.album_list, self.y_limit)

        for i, item in enumerate(max):
            self.screen.addstr(1 + i, 20, item, curses.A_BLINK)

class Get:

    #genre_list = ["fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self"]
    genre_list = [str(x) for x in range(100, 201)]
    album_list = ["fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self", "fuck", "your", "self"]

    def __init__(self):
        pass
    
    def get_albums(self, url):
        pass
    
def main(screen):

    menu = UI(screen)
    screen.clear()

    menu.display_genres()
    menu.display_albums()

    screen.refresh()
    screen.getch()

if __name__ == "__main__":
    curses.wrapper(main)
