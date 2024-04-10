import json
import os
import random
import string
import base64
import hashlib
import requests
import yaml
import jmespath
import logging

from . import database

from typing import Any, Iterable
from requests import Response
from flask import redirect, Flask
from flask import request as flask_request


logging.basicConfig(level=logging.INFO, 
                    handlers=[
                        logging.FileHandler('./logs/spotify.log'),
                        logging.StreamHandler(),
                        ]
                    )

app = Flask(__name__)

@app.route('/login')
def page():
    params = RequestsParameters.user_authorization()
    params = convert_params_to_query(params)
    return redirect('https://accounts.spotify.com/authorize' + params)


@app.route('/')
def get_code():

    code = flask_request.args.get('code') or ''

    if os.path.isfile("tokens.yaml"):
        token = YAML.retrieve_item("code")

        if token:
            return "Already has"
        elif code:
            YAML.write({"code": code})

    response = send_request(code)
    content = json.loads(response.content)
    tokens_dict = {key: content[key] for key in 
                   ["access_token", "refresh_token"]}

    YAML.write(tokens_dict)
    return "Great!"


def send_request(code: str) -> Response:

    params = RequestsParameters.access_token(code)

    return requests.post(
            'https://accounts.spotify.com/api/token',
            data=params['data'],
            headers=params['headers'],
    )


class YAML():

    YAML_FILE = 'tokens.yaml'

    @staticmethod
    def write(dct: dict[str, str]):
        with open(YAML.YAML_FILE, 'a') as file:
            yaml.dump(dct, file)

    @staticmethod
    def retrieve() -> dict[Any, Any]:
        with open(YAML.YAML_FILE, 'r') as file:
            content = yaml.safe_load(file)
        return content

    @staticmethod
    def retrieve_item(item: str) -> str:
        content = YAML.retrieve()
        return content[item]

    @staticmethod
    def update(dct: dict[Any, Any]):
        content = YAML.retrieve()

        for key in dct:
            content[key] = dct[key]

        with open(YAML.YAML_FILE, 'w') as file:
            yaml.dump(content, file)


def initcodes(cls):
    cls.generate_codes()
    return cls


@initcodes
class GetCodes():

    code_verifier = None
    code_challenge = None

    @classmethod
    def generate_codes(cls) -> None:
        if cls.code_verifier is not None:
            return

        rand = random.SystemRandom()
        code_verifier = ''.join(rand.choices(
                        string.ascii_letters + string.digits, k=128))

        code_sha_256 = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        b64 = base64.urlsafe_b64encode(code_sha_256)
        code_challenge = b64.decode('utf-8').replace('=', '') \
                                        .replace('+', '-').replace('/', '_')

        cls.code_verifier = code_verifier
        cls.code_challenge = code_challenge

class RequestsParameters():

    CLIENT_ID = 'bb47c973388a44ad90cbc25d837cada2'
    REDIRECT_URI = "https://127.0.0.1:5050"

    @staticmethod
    def user_authorization():
        return {"client_id": RequestsParameters.CLIENT_ID,
               "response_type": "code",
               "redirect_uri": RequestsParameters.REDIRECT_URI,
               "scope": "user-library-read",
               "code_challenge_method": "S256",
               "code_challenge": GetCodes.code_challenge}


    @staticmethod
    def access_token(code):
        return \
            {"headers":
               {"Content-Type":
                "application/x-www-form-urlencoded" },
             "data":
                   {"grant_type": "authorization_code",
                    "code" : code,
                    "redirect_uri": RequestsParameters.REDIRECT_URI,
                    "client_id": RequestsParameters.CLIENT_ID,
                    "code_verifier": GetCodes.code_verifier, 
                    }
               }

    @staticmethod
    def user_albums():
        return \
            {"headers":
                {"Authorization":
                    "Bearer " + YAML.retrieve_item('access_token')},
             "data":
                   {"limit": 50,
                    }
               }

    @staticmethod
    def refresh_token():
        return \
            {"headers":
               {"Content-Type":
                "application/x-www-form-urlencoded" },
             "data":
                   {"grant_type": "refresh_token",
                    "refresh_token" : YAML.retrieve_item('refresh_token'),
                    "client_id": RequestsParameters.CLIENT_ID,
                    }
             }

    @staticmethod
    def authorization_access():
        return \
            {"headers":
                {"Authorization":
                    "Bearer " + YAML.retrieve_item('access_token')}
             }



def convert_params_to_query(params: dict[Any, Any]) -> str:
    return '?' + ''.join(
            [str(x) + '=' + str(y) + '&' for x, y in params.items()])


def get_albums(url: str):
    logging.info("Trying to get albums")

    params = RequestsParameters.user_albums()

    if not url:
        data = convert_params_to_query(params['data'])
        url = 'https://api.spotify.com/v1/me/albums' + data

    response = requests.get(url,
                             headers=params['headers'],
                            )

    content = json.loads(response.content)

    if 'error' in content:
        #if status in content['error'] and 
        if content['error']['status'] == 401:
            raise ExpiredToken("Refresh the token")
        else:
            raise requests.HTTPError("Gave bad", content)
    return content


class ExpiredToken(Exception):
    pass


def refresh_token() -> bool:
    logging.info("Trying to refresh tokens")
    params = RequestsParameters.refresh_token()

    response = requests.post("https://accounts.spotify.com/api/token",
                             headers=params['headers'],
                             data=params['data']
                             )

    content = json.loads(response.content)

    if response.status_code == 200:
        YAML.update({"access_token": content['access_token'],
                     "refresh_token": content['refresh_token']})
        return True
    return False

        
def find_albums(albums: dict[Any, Any]) -> Iterable[Any]:
    return jmespath.search(
            'items[*].album.[name, artists[0].name, id]', albums)





def get_users_albums():
    url = ''
    refresh = False
    while True:
        try:
            user_albums = get_albums(url)
        except ExpiredToken:
            logging.warning("Needed to refresh")
            if refresh:
                break
            refresh_token()
            refresh = True
        else:
            logging.info("Requested user's albums")
            albums_temp = jmespath.search(
                    'items[*].album. \
                        {album: name, artist: artists[0].name, \
                         album_id: id, artist_id: artists[0].id}', \
                     user_albums)
            Get().add_temp(albums_temp)
            
            if user_albums['next']:
                logging.info("There's more albums, %s", user_albums['next'])
                url = user_albums['next']
            else:
                logging.info("Got them all")
                break

def get_genres():
    temp = Get().get_temp()
    artists_list = list(set(jmespath.search('[].artist_id', temp)))

    params = RequestsParameters.authorization_access()
    number_of_iterations = (-(-(len(artists_list)) // 50))  # round up
    print(lst_genres)
    breakpoint()

    for i in range(number_of_iterations):  # round up
        # for artist in artists_list[(i * 100):((i + 1) * 100)]:
        artists = '?ids=' + ','.join(artists_list[i * 50:(i + 1) * 50])
        response = requests.get(
            "https://api.spotify.com/v1/artists/" + artists,
             headers=params['headers'])

        content = json.loads(response.content)

        artists_dct = jmespath.search(
            'artists[*].{id: id, genres: genres}', content)

        database.Get().add_temp2(artists_dct)

def display_genres():
    temp = database.Get().get_temp()
    temp2 = database.Get().get_temp2()

    artists_albums = {}
    for i in temp:
        name = i['artist'] + ' - ' + i['album']
        if i['artist_id'] not in artists_albums:
            artists_albums[i['artist_id']] = [name]
        else:
            artists_albums[i['artist_id']].append(name)

    genres_artists = {}
    for item in temp2:
        for genre in item['genres']:
            if genre not in genres_artists:
                genres_artists[genre] = artists_albums[item['id']]
            else:
                genres_artists[genre].extend(artists_albums[item['id']])   

    return genres_artists

if __name__ == '__main__':
    is_authorized = YAML.retrieve_item("access_token")

    if not is_authorized:
        app.run(host="127.0.0.1", port=5050, debug=True, ssl_context='adhoc')

    logging.info("Is authorized")

    display_genres()
