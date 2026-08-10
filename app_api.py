import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi import Body
from typing import Optional

app = FastAPI()



class MovieCreate(BaseModel):
    title: str
    year: int

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[int] = None


def get_connection():
    conn = sqlite3.connect("movie.db")
    conn.row_factory = sqlite3.Row
    return conn   

def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            year INTEGER
        )
    """)
    conn.commit()
    conn.close()

create_table()



@app.post("/movies")
def create_movie(title: str, year: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO movies (title, year) VALUES (?, ?)",
        (title, year)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "title": title, "year": year}

@app.get("/movies/search")
def search_movies(title: str):
    conn = get_connection()
    cursor = conn.cursor()
    # LIKE with % wildcards lets this match partial titles too,
    # e.g. searching "bat" will find "Batman"
    cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f"%{title}%",))
    movies = cursor.fetchall()
    conn.close()
    return [dict(movie) for movie in movies]

@app.get("/movies")
def get_movies():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies")
    movies = cursor.fetchall()
    conn.close()
    return [dict(movie) for movie in movies]


@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    movie = cursor.fetchone()
    conn.close()

    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return dict(movie)




@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, title: str, year: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")

    cursor.execute(
        "UPDATE movies SET title = ?, year = ? WHERE id = ?",
        (title, year, movie_id)
    )
    conn.commit()
    conn.close()
    return {"id": movie_id, "title": title, "year": year}


@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM movies WHERE id = ?", (movie_id,))
    existing = cursor.fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")

    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()
    return {"message": f"Movie {movie_id} deleted"}