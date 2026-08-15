import aiosqlite
DB_NAME='Shop.db'

async def create_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    cases INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0,
    ban_reason TEXT DEFAULT ''
)
""")
        try:
            await db.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
        except Exception: pass
        try:
            await db.execute("ALTER TABLE users ADD COLUMN ban_reason TEXT DEFAULT ''")
        except Exception: pass
        await db.execute('CREATE TABLE IF NOT EXISTS inventory(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,country TEXT)')
        await db.execute('CREATE TABLE IF NOT EXISTS listings(id INTEGER PRIMARY KEY AUTOINCREMENT,country TEXT NOT NULL,price INTEGER NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        await db.execute('CREATE TABLE IF NOT EXISTS market_listings(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,country TEXT NOT NULL,price INTEGER NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        await db.execute('CREATE TABLE IF NOT EXISTS trades(id INTEGER PRIMARY KEY AUTOINCREMENT,sender_id INTEGER NOT NULL,receiver_id INTEGER NOT NULL,sender_country TEXT NOT NULL,status TEXT DEFAULT "pending",created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        await db.commit()

async def add_user(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR IGNORE INTO users(user_id) VALUES(?)',(uid,)); await db.commit()
async def get_balance(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT balance FROM users WHERE user_id=?',(uid,)); r=await c.fetchone(); return r[0] if r else 0
async def add_balance(uid,a):
    await add_user(uid)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET balance=balance+? WHERE user_id=?',(a,uid)); await db.commit()
async def get_inventory(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT country FROM inventory WHERE user_id=? ORDER BY id',(uid,)); return await c.fetchall()
async def add_country(uid,country):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT INTO inventory(user_id,country) VALUES(?,?)',(uid,country)); await db.commit()
async def remove_country(uid,country):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('DELETE FROM inventory WHERE id=(SELECT id FROM inventory WHERE user_id=? AND country=? LIMIT 1)',(uid,country)); await db.commit(); return c.rowcount>0
async def add_listing(country,price):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('INSERT INTO listings(country,price) VALUES(?,?)',(country,price)); await db.commit(); return c.lastrowid
async def get_listings():
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT id,country,price FROM listings ORDER BY id DESC'); r=await c.fetchall(); return [{'id':x[0],'country':x[1],'price':x[2]} for x in r]
async def get_listing(lid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT id,country,price FROM listings WHERE id=?',(lid,)); x=await c.fetchone(); return {'id':x[0],'country':x[1],'price':x[2]} if x else None
async def remove_listing(lid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('DELETE FROM listings WHERE id=?',(lid,)); await db.commit(); return c.rowcount>0
async def add_market_listing(uid,country,price):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('INSERT INTO market_listings(user_id,country,price) VALUES(?,?,?)',(uid,country,price)); await db.commit(); return c.lastrowid
async def get_market_listings():
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT id,user_id,country,price FROM market_listings ORDER BY id DESC'); r=await c.fetchall(); return [{'id':x[0],'user_id':x[1],'country':x[2],'price':x[3]} for x in r]
async def get_market_listing(lid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT id,user_id,country,price FROM market_listings WHERE id=?',(lid,)); x=await c.fetchone(); return {'id':x[0],'user_id':x[1],'country':x[2],'price':x[3]} if x else None
async def remove_market_listing(lid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('DELETE FROM market_listings WHERE id=?',(lid,)); await db.commit(); return c.rowcount>0
async def add_trade(sender,receiver,country):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('INSERT INTO trades(sender_id,receiver_id,sender_country) VALUES(?,?,?)',(sender,receiver,country)); await db.commit(); return c.lastrowid
async def get_trade(tid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT id,sender_id,receiver_id,sender_country,status FROM trades WHERE id=?',(tid,)); x=await c.fetchone(); return {'id':x[0],'sender_id':x[1],'receiver_id':x[2],'sender_country':x[3],'status':x[4]} if x else None
async def update_trade_status(tid,status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE trades SET status=? WHERE id=?',(status,tid)); await db.commit()

async def set_ban(uid, banned, reason=''):
    await add_user(uid)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('UPDATE users SET banned=?, ban_reason=? WHERE user_id=?',(1 if banned else 0, reason, uid)); await db.commit()

async def get_ban(uid):
    async with aiosqlite.connect(DB_NAME) as db:
        c=await db.execute('SELECT banned,ban_reason FROM users WHERE user_id=?',(uid,)); r=await c.fetchone(); return (bool(r[0]), r[1] or '') if r else (False,'')
