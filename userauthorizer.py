import sqlite3


class Authorizer:
    def __init__(self):
        with sqlite3.connect("users.db") as db:
            cur = db.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS users(userId INTEGER, platform TEXT, platformId TEXT)"
            )

    def checkAuth(self, userId: int):
        ### userId - айди пользователя в Telegram.
        with sqlite3.connect("users.db") as db:
            cur = db.cursor()
            cur.execute(
                "SELECT platform, platformId FROM users WHERE userId = ?", (userId,)
            )
            all_users = cur.fetchall()
            try:
                last_info = all_users[-1]
                return last_info
            except Exception:
                return 0

    def createAuth(self, userId: int, platform: str, platformId: str):
        with sqlite3.connect("users.db") as db:
            cur = db.cursor()
            cur.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (
                    userId,
                    platform,
                    platformId,
                ),
            )

    def removeAllAuths(self, userId):
        with sqlite3.connect("users.db") as db:
            cur = db.cursor()
            cur.execute("DELETE FROM users WHERE userId = ?", (userId,))
