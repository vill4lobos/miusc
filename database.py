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

    def save(self):
        r = requests.get(
            "http://musicbrainz.org/ws/2/release-group/" +
            "?query=artist:%22truckfighters%22&fmt=json").json()

        fltr = jmespath.search(
            '"release-groups"[?"primary-type"==`Album`].\
            [tags[0].name, title]', r)

        with shelve.open(self.DB_PATH, writeback=True) as db:
            for item in fltr:
                if item[0] in db["genres"].keys():
                    if item[1] in db['genres'][item[0]]:
                        continue
                    db['genres'][item[0]].append(item[1])
                else:
                    db['genres'].update({item[0]: [item[1]]})

    def get(self):
        with shelve.open(self.DB_PATH) as db:
            return list(db.items())
