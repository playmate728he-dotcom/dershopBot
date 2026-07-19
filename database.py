import aiosqlite

DB = "shop.db"

async def create_db():
    async with aiosqlite.connect(DB) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            cases INTEGER DEFAULT 0
        )
        """)
        await db.commit()


async def add_user(user_id, username):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users(user_id, username) VALUES(?, ?)",
            (user_id, username)
        )
        await db.commit()


async def get_cases(user_id):
    async with aiosqlite.connect(DB) as db:
        cur = await db.execute(
            "SELECT cases FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0] if row else 0


async def add_cases(user_id, amount):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            "UPDATE users SET cases=cases+? WHERE user_id=?",
            (amount, user_id)
        )
        await db.commit()


async def remove_case(user_id):
    async with aiosqlite.connect(DB) as db:
        await db.execute(
            """
            UPDATE users
            SET cases = cases - 1
            WHERE user_id=? AND cases>0
            """,
            (user_id,)
        )
        await db.commit()