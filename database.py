import aiosqlite

DB_NAME = "Shop.db"


async def create_db():
    await create_promocodes()

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            balance INTEGER DEFAULT 0,
            cases INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            country TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promocodes(
            code TEXT PRIMARY KEY,
            reward INTEGER,
            uses INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_used(
            user_id INTEGER,
            code TEXT
        )
        """)

        await db.commit()

async def create_promocodes():

    async with aiosqlite.connect("shop.db") as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promocodes(

            code TEXT PRIMARY KEY,

            reward INTEGER,

            reward_type TEXT,

            uses INTEGER
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS promo_users(

            user_id INTEGER,

            code TEXT
        )
        """)

        await db.commit()

async def add_user(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "INSERT OR IGNORE INTO users(user_id) VALUES(?)",
            (user_id,)
        )

        await db.commit()


async def get_balance(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        return row[0] if row else 0


async def add_balance(user_id, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "UPDATE users SET balance=balance+? WHERE user_id=?",
            (amount, user_id)
        )

        await db.commit()


async def get_cases(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT cases FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cur.fetchone()

        return row[0] if row else 0


async def add_case(user_id, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "UPDATE users SET cases=cases+? WHERE user_id=?",
            (amount, user_id)
        )

        await db.commit()


async def remove_case(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "UPDATE users SET cases=cases-1 WHERE user_id=?",
            (user_id,)
        )

        await db.commit()


async def add_country(user_id, country):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            "INSERT INTO inventory(user_id,country) VALUES(?,?)",
            (user_id, country)
        )

        await db.commit()


async def get_inventory(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT country FROM inventory WHERE user_id=?",
            (user_id,)
        )
 
      
        return await cur.fetchall()
    
async def remove_country(user_id, country):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM inventory
            WHERE id = (
                SELECT id
                FROM inventory
                WHERE user_id=? AND country=?
                LIMIT 1
            )
            """,
            (user_id, country)
        )

        await db.commit()


async def create_promo(code, reward, reward_type, uses):

    async with aiosqlite.connect("shop.db") as db:

        await db.execute(
            """
            INSERT INTO promocodes
            VALUES(?,?,?,?)
            """,
            (code, reward, reward_type, uses)
        )

        await db.commit()


async def get_promo(code):

    async with aiosqlite.connect("shop.db") as db:

        cursor = await db.execute(
            """
            SELECT * FROM promocodes
            WHERE code=?
            """,
            (code,)
        )

        return await cursor.fetchone()


async def activate_promo(user_id, code):

    async with aiosqlite.connect("shop.db") as db:

        cursor = await db.execute(
            """
            SELECT *
            FROM promo_users

            WHERE
            user_id=?
            AND code=?
            """,
            (user_id, code)
        )

        if await cursor.fetchone():
            return False

        await db.execute(
            """
            INSERT INTO promo_users
            VALUES(?,?)
            """,
            (user_id, code)
        )

        await db.commit()

        return True

async def use_promo(code):

    async with aiosqlite.connect("shop.db") as db:

        await db.execute(
            """
            UPDATE promocodes

            SET uses = uses - 1

            WHERE code = ?
            """,
            (code,)
        )

        await db.commit()