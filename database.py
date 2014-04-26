import sqlite3 as sql


class database(object):
    con = None
    connected = False
    retry = 0

    def __init__(self):
        self.connect()
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS `client` (
                steam_id text,
                class_name text,
                level integer DEFAULT 1,
                experience integer DEFAULT 0,
                PRIMARY KEY(steam_id, class_name)
            )
        """)

    def connect(self):
        self.con = sql.connect('srpg.db')

    def close(self):
        if self.connected:
            self.con.close()

    def getConnection(self):
        return self.con

    def getCursor(self):
        return self.con.cursor()
