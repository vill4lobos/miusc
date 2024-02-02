import requests
import jmespath
from tinydb import TinyDB, where
from typing import Iterable


class Database:
    """
    Kind of an abstract class to guide its subclasses
    """
    def __init__(self):
        self.DB_PATH = "./database/data.json"

    def add_discography(self, lst: Iterable[str], artist: str) -> None:
        """Add all elements of $lst in the database"""
        raise NotImplementedError

    def add_artist(self, str: str) -> None:
        """Add $artist in the table artist"""
        raise NotImplementedError

    def get_all_albums(self) -> list[dict]:
        """Return all albums in the genres table"""
        raise NotImplementedError

    def exists_artist(self) -> bool:
        """Return True if $artist exists"""
        raise NotImplementedError


class NoSQL(Database):
    """
    Used to connect and interact with TinyDB

    Attr:
    self.db : TinyDB()
    """
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.db = TinyDB(self.DB_PATH)

        self.tb_genres = self.db.table('genres')
        self.tb_artists = self.db.table('genres')

    def create_tables(self) -> None:
        """Create the following tables if the database doesn't have it
         already"""
        if 'genres' not in self.db.tables():
            self.db.table('genres')
        if 'artist' not in self.db.tables():
            self.db.table('artist')

    def add_discography(self, lst: Iterable[str], artist: str) -> None:
        for album in lst:
            if self.tb_genres.search(where(album[0]).exists()):
                self.tb_genres.update(
                    lambda docs: docs[album[0]].append(album[1]),
                    where(album[0]).exists())
            else:
                self.tb_genres.insert({album[0]: [album[1]]})

        self.add_artist(artist)

    def add_artist(self, artist: str) -> None:
        if not self.tb_artists.search(where('artists').any([artist])):
            self.tb_artists.update(
                lambda docs: docs['artists'].append(artist),
                where('artist').exists())

    def get_all_albums(self: str) -> list[dict]:
        return self.tb_genres.all()

    def exists_artist(self, artist: str) -> bool:
        return True if artist in self.tb_artists.all() else False


class SQL(Database):
    pass


class Get:
    """
    Used to make requests to the databases

    Attr:
    self.dbs_dict : dict[string, class]
    Indicate which Database() subclass will be used
    """

    def __init__(self):
        self.default_artist_lists = \
            ['truckfighters', 'kyuss', 'sleep', 'damad', 'corrupted']
        self.dbs_dict = {'sql': SQL(), 'nosql': NoSQL()}

        self.db = self.dbs_dict['nosql']

        if len(self.db.get_all_albums()) < 8:
            self.populate_db()

    def request_albums(self, artist: str) -> list:
        """Request all albums of an $artist, filter it and return"""
        r = requests.get(
            "http://musicbrainz.org/ws/2/release-group/" +
            "?query=artist:%22{}%22&fmt=json".format(artist)).json()

        fltr = jmespath.search(
            '"release-groups"[?"primary-type"==`Album`].\
            [tags[0].name, title]', r)

        return fltr

    def populate_db(self) -> None:
        """Insert default values in the database if it's the first use"""
        for artist in self.default_artist_lists:
            if not self.db.exists_artist(artist):
                discography = self.request_albums(artist)
                self.db.add_discography(
                    self.change_none_to_undefined(discography), artist)

    def change_none_to_undefined(self, lst: Iterable) -> list:
        """Change every None element inside a nested list  to 'undefined'"""
        return [list(map(lambda x: 'undefined' if x is None else x, sub_lst))
                for sub_lst in lst]

    def force_alpha_string(self, str: str) -> str:
        """Remove any non-alphanumeric character from a string"""
        return ''.join(filter(str.isalpha, str))

    def get_all_albums(self) -> list[dict]:
        return self.db.get_all_albums()

    def add_artist(self):
        pass

    def wrap_response(self):
        pass
