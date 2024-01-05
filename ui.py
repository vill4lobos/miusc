import curses
from functools import reduce

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

    def genres_x(self):
        lst = self.max_albums(Get.genre_list, self.x_limit)

        center = self.center_str(lst[0])
        left = center
        right = center #+ len(lst[0])

        lst_width = [center]
        new_genre_list = [lst[0]]
        lst.pop(0)

        #left, right, center = 0, 0, 0

        #for i, item in enumerate(lst):

        i, j, b = 0, 0, True
        while i < len(lst) - 1:
            b = not b
            i += 1

            if b:
                right = right + len(lst[j]) + self.GENRE_SEPARATE

                if right >= self.x_limit:
                    j += 1
                    continue

                lst_width.append(right)
                new_genre_list.append(lst[j])
                j += 1

            else: 
                left = left - len(lst[-j]) - self.GENRE_SEPARATE
                if left <= 0:
                    continue

                lst_width.append(left)
                new_genre_list.append(lst[-j])
            

        return zip(lst_width, new_genre_list)
        


        
        



    def display_genres(self):
        #len_genre = 0
        lst_genres = self.genres_x()
        #lst_genres = self.generate_genres()

        #debug()
        for i, item in lst_genres:
            self.screen.addstr(0, i, item,
                                curses.A_ITALIC)
            #len_genre += len(item) + 2

    def display_albums(self):
        max = self.max_albums(Get.album_list, self.y_limit)

        for i, item in enumerate(max):
            self.screen.addstr(1 + i, 20, item, curses.A_BLINK)

        #reduce(lambda i, x: x[1] + i if x[1] + i < 30 else x[0], kk, 0)

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