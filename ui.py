import curses
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

    """
    Returns a list of tuples with all elements and their lengths that can fit
    at max x.length of terminal with index[0] at the middle of the list
    """
    # TODO: fix list out of range when more than 90 movements in the same direction
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
        max = self.max_albums(Get.album_list, self.y_limit)

        for i, item in enumerate(max):
            self.screen.addstr(1 + i, 20, item, curses.A_BLINK)

    def navigate(self, b):
        self.position += 1 if b else -1


class Get:

    genre_list = [str(x) for x in range(100, 201)]
    album_list = ["fuck", "your", "selfffff", "fuck", "your", "self", "fuck",
                  "your", "self", "fuck", "your", "self", "fuck", "your",
                  "self"]

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
