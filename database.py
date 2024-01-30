import requests
import jmespath
import shelve

# from tinydb import TinyDB, Query
# db = TinyDB('./db.json')
# Album = Query()


class Database:

    def __init__(self):

        self.DB_PATH = "./database/data.db"

        with shelve.open(self.DB_PATH) as db:
            if not list(db.keys()):
                db["genres"] = {}
            if 'artists' not in list(db.keys()):
                db["artists"] = {}

    def save_albums(self, dict, artist):
        with shelve.open(self.DB_PATH, writeback=True) as db:
            for item in dict:
                if item[0] in db["genres"].keys():
                    if item[1] in db['genres'][item[0]]:
                        continue
                    db["genres"][item[0]].append(item[1])
                else:
                    if item[0] is None:
                        item[0] = 'undefined'
                    db["genres"].update({item[0]: [item[1]]})

            db["artists"].update({'artists': artist})

    def get_all(self):
        with shelve.open(self.DB_PATH) as db:
            return db["genres"]

    def get_artist(self, artist):
        with shelve.open(self.DB_PATH) as db:
            return True if artist in db['artists'] else False


class Get:

    def __init__(self):

        self.default_artist_lists = \
            ['truckfighters', 'kyuss', 'sleep', 'damad', 'corrupted']

        self.db = Database()

        # TODO: populate db if 50 entries or less

    def get_albums(self, artist):

        artist = ''.join(filter(str.isalpha, artist))
        if self.db.get_artist(artist):
            return "Already exists"

        r = requests.get(
            "http://musicbrainz.org/ws/2/release-group/" +
            "?query=artist:%22{}%22&fmt=json".format(artist)).json()

        fltr = jmespath.search(
            '"release-groups"[?"primary-type"==`Album`].\
            [tags[0].name, title]', r)

        self.db.save_albums(fltr, artist)

        return fltr

    def default_get_albums(self):
        rtn_lst = []

        for item in self.default_artist_lists:
            rtn_lst.append(self.get_albums(item))

        return rtn_lst

    def get_all_albums(self):
        return self.db.get_all()
