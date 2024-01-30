from flask import Flask, redirect, url_for
from database import Database

app = Flask(__name__)
app.config["DEBUG"]

db = Database()


@app.route("/")
def hello():
    db.save()
    return "'Sup!"


@app.route("/genres", methods=["GET"])
def genres():
    return db.get()


@app.route("/save", methods=["GET"])
def save():
    db.save()
    return redirect(url_for('genres'))


if __name__ == "__main__":
    app.run(debug=True)
