from flask import Flask, redirect, url_for
from database import Get
#from livereload import Server

app = Flask(__name__)
app.config["DEBUG"]

db = Get()


@app.route("/")
def hello():
    return "'Sup!"


@app.route("/genres", methods=["GET"])
def genres():
    return db.default_get_albums()


@app.route("/all", methods=["GET"])
def get_all():
    return db.get_all_albums()


@app.route("/save", methods=["GET"])
def save():
    return redirect(url_for('genres'))


if __name__ == "__main__":
    app.run(debug=True)
