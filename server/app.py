#!/usr/bin/env python3
from aiohttp import web
from os import mkdir
from datetime import datetime
from pathlib import Path
import logging
import sys
import sqlite3

"""
Logging Stuff
"""

try:
    mkdir(".logs")
except FileExistsError:
    pass

fp = f'./.logs/{datetime.now()}.log'.replace(' ', '-')

if sys.platform.lower() == 'win32':
    fp = fp.replace(':', '.')


logger = logging.getLogger()
logger.setLevel(logging.DEBUG) # we don't want to filter messages yet

fh = logging.FileHandler(fp)
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO) # we don't want to clog up the console

fmt = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] : %(message)s')

ch.setFormatter(fmt)
fh.setFormatter(fmt)

logger.addHandler(ch)
logger.addHandler(fh)

"""
Database Stuff
"""
class DatabaseHandler():
    """
    A simple database wrapper that
    manages an sqlite database
    """

    def __init__(self, db_path):
        self.connection = sqlite3.connect(db_path)
        cursor = self.get_cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                           userid INTEGER PRIMARY KEY,
                           name TEXT NOT NULL UNIQUE
                       );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS entries(
                            entryid    INTEGER PRIMARY KEY,
                            user       INTEGER NOT NULL,
                            timetaken  INTEGER NOT NULL,
                            FOREIGN KEY (user) REFERENCES users(id)
                       );""")
        self.commit()

    def __del__(self):
        self.commit()
        self.connection.close()

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        return self.connection.commit()


    def has_user(self, username):
        cur = self.get_cursor()
        res = cur.execute("SELECT 1 FROM users WHERE name=?;", (username,))
        return bool(res.fetchall())

    def get_user_id(self, username):
        cur = self.get_cursor()
        res = cur.execute("SELECT userid FROM users WHERE name=?;", (username,))
        return res.fetchall()[0][0]

    def get_username(self, userid):
        cur = self.get_cursor()
        res = cur.execute("SELECT name FROM users WHERE userid=?;", (userid,))
        return res.fetchall()[0][0]

    def get_entries(self):
        cur = self.get_cursor()
        res = cur.execute("SELECT * FROM entries ORDER BY timetaken ASC;", [])
        response = []
        for result in res.fetchall():
            response.append({
                "entryid": result[0],
                "user": {
                    "id": result[1],
                    "name": self.get_username(result[1])
                },
                "timetaken": result[2]
            })
        return response


    def add_user(self, username):
        if self.has_user(username):
            return False
        cur = self.get_cursor()
        cur.execute("INSERT INTO users(name) VALUES (?);", (username,))
        self.commit()
        return True

    def add_entry(self, userid, timetaken):
        cur = self.get_cursor()
        cur.execute(
            "INSERT INTO entries(user, timetaken) VALUES (?, ?);",
            (userid, timetaken)
        )
        self.commit()





"""
AIOHTTP Stuff
"""

routes = web.RouteTableDef()

@routes.post('/api/users')
async def add_user(request):
    db = request.app["database"]
    json = await request.json()
    username = json["name"]
    if db.add_user(username):
        return web.HTTPCreated()
    else:
        return web.HTTPConflict()

@routes.post('/api/entries')
async def add_entry(request):
    db = request.app["database"]
    json = await request.json()

    if "name" in json:
        userid = db.get_user_id(json["name"])
    else:
        userid = json["userid"]

    timetaken = json["timetaken"]

    db.add_entry(userid, timetaken)
    return web.HTTPCreated()

@routes.get('/api/entries')
async def get_entries(request):
    db = request.app["database"]
    resp = db.get_entries()
    logger.info(resp)
    return web.json_response(resp)


@web.middleware
async def static_server(request, handler):

    rel_fp = Path(request.path).relative_to('/')
    fp = Path('./static') / rel_fp

    if fp.is_dir(): # somebody is looking for /
        fp /= 'index.html'

    if not fp.exists():
        return await handler(request)

    return web.FileResponse(fp)

if __name__ == '__main__':
    app = web.Application(middlewares=[static_server])
    app["database"] = DatabaseHandler("./database.db")
    app.add_routes(routes)
    web.run_app(app, port=9000)




