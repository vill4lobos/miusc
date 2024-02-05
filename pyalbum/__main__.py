from flask import Flask
import curses
import threading
import yaml
import sys

import ui
from api import api


def run():
    app = Flask(__name__)
    app.register_blueprint(api)

    if __name__ == '__main__':
        app.run()  # debug=True)


with open('pyalbum/config.yaml', 'r') as stream:
    cfg = yaml.safe_load(stream)

# TODO: use celery
if cfg["run_api"] and (len(sys.argv) - 1 > 1):
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()

if cfg["run_ui"]:
    curses.wrapper(ui.main)
