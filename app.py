"""A separate Flask web app for generating and saving quotes."""

from __future__ import annotations

import os
import random
import sqlite3
from contextlib import closing
from pathlib import Path

from flask import Flask, flash, redirect, render_template, session, url_for


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "quotes.sqlite3"
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "codealpha-quotes-local-key")

SEED_QUOTES = [
    ("A little progress still moves you forward.", "CodeAlpha Quote Pack"),
    ("Make room for the work that matters.", "CodeAlpha Quote Pack"),
    ("Curiosity turns a question into a journey.", "CodeAlpha Quote Pack"),
    ("Consistency makes small efforts add up.", "CodeAlpha Quote Pack"),
    ("Begin with what you know and learn the rest.", "CodeAlpha Quote Pack"),
    ("A clear goal gives your next step a direction.", "CodeAlpha Quote Pack"),
    ("Rest is part of a good rhythm.", "CodeAlpha Quote Pack"),
    ("The best time to practice is the time you can keep.", "CodeAlpha Quote Pack"),
    ("Good ideas grow when you give them attention.", "CodeAlpha Quote Pack"),
    ("Finish one useful thing, then choose the next.", "CodeAlpha Quote Pack"),
]


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def initialize_database() -> None:
    with closing(connect()) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS quotes "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT NOT NULL, author TEXT NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS favorites "
            "(quote_id INTEGER PRIMARY KEY, FOREIGN KEY (quote_id) REFERENCES quotes(id) ON DELETE CASCADE)"
        )
        if db.execute("SELECT COUNT(*) FROM quotes").fetchone()[0] == 0:
            db.executemany("INSERT INTO quotes (text, author) VALUES (?, ?)", SEED_QUOTES)
        db.commit()


initialize_database()


def favorite_ids() -> set[int]:
    with closing(connect()) as db:
        return {row[0] for row in db.execute("SELECT quote_id FROM favorites")}


@app.get("/")
def index():
    quote_id = session.get("last_quote_id")
    if quote_id is not None:
        with closing(connect()) as db:
            quote = db.execute("SELECT id, text, author FROM quotes WHERE id = ?", (quote_id,)).fetchone()
    else:
        quote = None

    if quote is None:
        with closing(connect()) as db:
            choices = db.execute("SELECT id, text, author FROM quotes ORDER BY id").fetchall()
        quote = random.choice(choices) if choices else None
    if quote is not None:
        session["last_quote_id"] = quote["id"]
    return render_template("index.html", quote=quote, favorites=favorite_ids())


@app.get("/new")
def new_quote():
    last_id = session.get("last_quote_id")
    with closing(connect()) as db:
        choices = db.execute(
            "SELECT id FROM quotes WHERE id != ? ORDER BY id", (last_id or -1,)
        ).fetchall()
        if not choices:
            choices = db.execute("SELECT id FROM quotes ORDER BY id").fetchall()
    if choices:
        session["last_quote_id"] = random.choice(choices)["id"]
    return redirect(url_for("index"))


@app.post("/favorite/<int:quote_id>")
def toggle_favorite(quote_id: int):
    with closing(connect()) as db:
        exists = db.execute("SELECT 1 FROM quotes WHERE id = ?", (quote_id,)).fetchone()
        if exists:
            saved = db.execute("SELECT 1 FROM favorites WHERE quote_id = ?", (quote_id,)).fetchone()
            if saved:
                db.execute("DELETE FROM favorites WHERE quote_id = ?", (quote_id,))
                flash("Removed from favorites.", "success")
            else:
                db.execute("INSERT INTO favorites (quote_id) VALUES (?)", (quote_id,))
                flash("Saved to favorites.", "success")
            db.commit()
    session["last_quote_id"] = quote_id
    return redirect(url_for("index"))


@app.get("/favorites")
def favorites_page():
    with closing(connect()) as db:
        quotes = db.execute(
            "SELECT q.id, q.text, q.author FROM quotes q "
            "JOIN favorites f ON f.quote_id = q.id ORDER BY q.id DESC"
        ).fetchall()
    return render_template("favorites.html", quotes=quotes, favorites=favorite_ids())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5002")), debug=False)
