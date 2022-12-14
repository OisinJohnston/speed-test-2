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
        cursor.execute("""CREATE TABLE IF NOT EXISTS singleentries(
                            entryid    INTEGER PRIMARY KEY,
                            user       INTEGER NOT NULL,
                            timetaken  INTEGER NOT NULL,
                            FOREIGN KEY (user) REFERENCES users(id)
                       );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS twoentries(
                    entryid   INTEGER PRIMARY KEY,
                    userone   INTEGER NOT NULL,
                    usertwo   INTEGER NOT NULL,
                    winner    INTEGER NOT NULL,
                    winnerscr INTEGER NOT NULL,
                    FOREIGN KEY (userone) REFERENCES users(id),
                    FOREIGN KEY (usertwo) REFERENCES users(id),
                    FOREIGN KEY (winner)  REFERENCES users(id)
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

    def get_singleentries(self):
        cur = self.get_cursor()
        res = cur.execute("SELECT * FROM singleentries ORDER BY timetaken ASC;", [])
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

    def get_twoentries(self):
        cur = self.get_cursor()
        res = cur.execute("SELECT * FROM twoentries ORDER BY timetaken ASC;", [])
        response = []
        for result in res.fetchall():
            response.append({
                "entryid": result[0],
                "player 1": self.get_username(result[1]),
                "player 2": self.get_username(result[2]),
                "winner": self.get_username(result[3]),
                "winnerscr": result[4]
            })
        return response


    def add_user(self, username):
        if self.has_user(username):
            return False
        cur = self.get_cursor()
        cur.execute("INSERT INTO users(name) VALUES (?);", (username,))
        self.commit()
        return True

    def add_singleentry(self, userid, timetaken):
        cur = self.get_cursor()
        cur.execute(
            "INSERT INTO singleentries(user, timetaken) VALUES (?, ?);",
            (userid, timetaken)
        )
        self.commit()

    def add_twoentry(self, players, winner, winnerscore):
        player1, player2 = players
        cur = self.get_cursor()
        cur.execute(
                    "INSERT INTO twoentries(userone, usertwo, winner, winnerscr) VALUES (?, ?, ?, ?) ",
                    (player1, player2, winner, winnerscore)
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

@routes.post('/api/singleentries')
async def add_singleentry(request):
    db = request.app["database"]
    json = await request.json()

    if "name" in json:
        userid = db.get_user_id(json["name"])
    else:
        userid = json["userid"]

    timetaken = json["timetaken"]

    db.add_singleentry(userid, timetaken)
    return web.HTTPCreated()

@routes.post('/api/twoentries')
async def add_twoentry(request):
    db = request.app["database"]
    json = await request.json()

    players = [db.get_user_id(name) for name in json["names"]]
    winner = db.get_user_id(json["winner"])
    winnerscr = json["winnerscr"]
    db.add_twoentry(players, winner, winnerscr)
    return web.HTTPCreated()

@routes.get('/api/singleentries')
async def get_singleentries(request):
    db = request.app["database"]
    resp = db.get_singleentries()
    logger.info(resp)
    return web.json_response(resp)

@routes.get('/api/twoentries')
async def get_twoentries(request):
    db = request.app["database"]
    resp = db.get_twoentries()
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




