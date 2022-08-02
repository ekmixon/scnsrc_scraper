#!/usr/bin/python
import os
import re
import requests
import sqlite3 as sql

# pip install parse-torrent-name
try:
    import PTN
except ImportError:
    print "[!] Failed to import PTN, please run 'pip install parse-torrent-name'"
    exit(-2)

SQL_DB_LOCATION = os.path.join(os.getcwd(), "scraper.sqlite")

class Connection:

    def __init__(self, db_location):
        self.db_location = db_location
        if not os.path.isfile(self.db_location):
            self.__setup_db__()

        self.connection = self.create_connection()
    
    def __setup_db__(self):
        conn = self.create_connection()
        with conn:
            conn.execute("CREATE TABLE movies (name PRIMARY KEY, movie_title TEXT UNIQUE)")
        
    def create_connection(self):
        """ create a database connection to a SQLite database """
        try:
            connection = sql.connect(self.db_location)
        except sql.Error as e:
            print(e)
            return False
        else:
            return connection
    
    def close_connection(self):
        self.connection.close()
    
    def add_movie(self, name, title):
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT * FROM movies WHERE name=?", (name,))
            if cur.fetchone() is not None:
                return False

            cur.execute("SELECT * FROM movies WHERE movie_title=?", (title,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO movies VALUES (?, ?)", (name, title))
            return True
            

def scrap_page(c=Connection(SQL_DB_LOCATION)):
    url = "https://www.scnsrc.me/category/films/bluray/page/"
    count = 1

    while True:
        url = f"https://www.scnsrc.me/category/films/bluray/page/{count}/"
        count += 1

        if count > 200:
            break

        url = "https://www.scnsrc.me/category/films/bluray/page/{}/".format(count)
        req = requests.get(url)

        if req.status_code != 200:
            print(f"[!] Recieved {req.status_code} from {url}... exiting")
            exit(-1)

        movie_list = [".".join(movie.split()).lower() for movie in re.findall("title=\"Goto (.*?)\"", req.text)]

        for movie in movie_list:
            if "1080" not in movie:
                continue

            if not c.add_movie(movie, get_movie_title(movie)):
                return


def get_movie_title(movie):
    info = PTN.parse(movie)
    try:
        return info['title']
    except KeyError:
        return " ".join(movie.split("."))


if __name__ == "__main__":
    scrap_page()

