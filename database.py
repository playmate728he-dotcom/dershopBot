import aiosqlite

DB_NAME = "database.db"


async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            username TEXT,

            balance INTEGER DEFAULT 0,

            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,

            pepe_cases INTEGER DEFAULT 0,
            samsa_cases INTEGER DEFAULT 0,
            der_cases INTEGER DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            country TEXT,
            price INTEGER
        )
        """)

        await db.commit()


async def add_user(user_id, username):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT OR IGNORE INTO users(user_id,username)
            VALUES(?,?)
            """,
            (user_id, username)
        )
        await db.commit()


async def get_balance(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT balance FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0]


async def add_balance(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET balance = balance + ?
            WHERE user_id=?
            """,
            (amount, user_id)
        )
        await db.commit()


async def get_xp(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT xp FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0]


async def add_xp(user_id, amount):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE user_id=?
            """,
            (amount, user_id)
        )
        await db.commit()


async def get_level(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT level FROM users WHERE user_id=?",
            (user_id,)
        )
        row = await cur.fetchone()
        return row[0]


async def set_level(user_id, level):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET level=?
            WHERE user_id=?
            """,
            (level, user_id)
        )
        await db.commit()


async def add_country(user_id, country, price):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO inventory(user_id,country,price)
            VALUES(?,?,?)
            """,
            (user_id, country, price)
        )
        await db.commit()


async def get_inventory(user_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT id,country,price
            FROM inventory
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        return await cur.fetchall()

async def add_case(user_id, case_type, amount):

    async with aiosqlite.connect(DB_NAME) as db:

        if case_type == "pepe":
            await db.execute(
                "UPDATE users SET pepe_cases=pepe_cases+? WHERE user_id=?",
                (amount, user_id)
            )

        elif case_type == "samsa":
            await db.execute(
                "UPDATE users SET samsa_cases=samsa_cases+? WHERE user_id=?",
                (amount, user_id)
            )

        elif case_type == "der":
            await db.execute(
                "UPDATE users SET der_cases=der_cases+? WHERE user_id=?",
                (amount, user_id)
            )

        await db.commit()


async def get_cases(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            """
            SELECT pepe_cases,samsa_cases,der_cases
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )
        return await cur.fetchone()


async def remove_case(user_id, case_type):

     async with aiosqlite.connect(DB_NAME) as db:

        if case_type == "pepe":
            await db.execute(
                "UPDATE users SET pepe_cases=pepe_cases-1 WHERE user_id=?",
                (user_id,)
            )

        elif case_type == "samsa":
            await db.execute(
                "UPDATE users SET samsa_cases=samsa_cases-1 WHERE user_id=?",
                (user_id,)
            )

        elif case_type == "der":
            await db.execute(
                "UPDATE users SET der_cases=der_cases-1 WHERE user_id=?",
                (user_id,)
            )

        await db.commit()


async def buy_case_balance(user_id, price):

    balance = await get_balance(user_id)

    if balance < price:
        return False

    await add_balance(user_id, -price)

    return True
async def get_item(item_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT id,user_id,country,price
            FROM inventory
            WHERE id=?
            """,
            (item_id,)
        )

        return await cur.fetchone()
    


    async def delete_item(item_id):

     async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            DELETE FROM inventory
            WHERE id=?
            """,
            (item_id,)
        )

        await db.commit()
async def create_promo(code, reward, uses):

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO promocodes
            VALUES(?,?,?)
            """,
            (code, reward, uses)
        )

        await db.commit()


async def activate_promo(user_id, code):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT reward,uses FROM promocodes WHERE code=?",
            (code,)
        )

        promo = await cur.fetchone()

        if promo is None:
            return "notfound"

        reward, uses = promo

        cur = await db.execute(
            """
            SELECT *
            FROM promo_used
            WHERE user_id=? AND code=?
            """,
            (user_id, code)
        )

        used = await cur.fetchone()

        if used:
            return "used"

        if uses <= 0:
            return "ended"

        await db.execute(
            "UPDATE promocodes SET uses=uses-1 WHERE code=?",
            (code,)
        )

        await db.execute(
            "INSERT INTO promo_used VALUES(?,?)",
            (user_id, code)
        )

        await db.commit()

        return reward
    
async def sell_item(item_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            """
            SELECT user_id,price
            FROM inventory
            WHERE id=?
            """,
            (item_id,)
        )

        item = await cur.fetchone()

        if item is None:
            return False

        user_id, price = item

        reward = int(price * 0.65)

        await db.execute(
            "DELETE FROM inventory WHERE id=?",
            (item_id,)
        )

        await db.execute(
            """
            UPDATE users
            SET balance=balance+?
            WHERE user_id=?
            """,
            (reward, user_id)
        )

        await db.commit()

        return reward
    
async def get_stats():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT COUNT(*) FROM users"
        )
        users = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT COUNT(*) FROM inventory"
        )
        inventory = (await cur.fetchone())[0]

        cur = await db.execute(
            "SELECT IFNULL(SUM(balance),0) FROM users"
        )
        balance = (await cur.fetchone())[0]

        cur = await db.execute(
            """
            SELECT
            IFNULL(SUM(pepe_cases),0),
            IFNULL(SUM(samsa_cases),0),
            IFNULL(SUM(der_cases),0)
            FROM users
            """
        )

        pepe, samsa, der = await cur.fetchone()

        return (
            users,
            inventory,
            balance,
            pepe,
            samsa,
            der
        )
async def get_all_users():

    async with aiosqlite.connect(DB_NAME) as db:

        cur = await db.execute(
            "SELECT user_id FROM users"
        )

        return await cur.fetchall()
    