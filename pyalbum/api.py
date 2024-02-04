from flask import redirect, url_for, Blueprint
from database import Get

api = Blueprint('api', __name__)
db = Get()


@api.route("/")
def root():
    return "'Sup!"


@api.route("/genres", methods=["GET"])
def genres():
    return db.get_all_albums()


@api.route("/all", methods=["GET"])
def get_all():
    return db.get_all_albums()


@api.route("/save", methods=["GET"])
def save():
    return redirect(url_for('genres'))
