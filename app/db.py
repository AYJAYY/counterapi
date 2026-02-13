import aiosqlite

DB_PATH = "counter.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS counters (
                name TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.commit()

async def get_counter(name: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT name, count, created_at FROM counters WHERE name = ?", (name,)
        ) as cursor:
            row = await cursor.fetchone()
            if row is None:
                return None
            return {"name": row["name"], "count": row["count"], "created_at": row["created_at"]}

async def create_counter(name: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO counters (name) VALUES (?)", (name,))
        await db.commit()
    return await get_counter(name)

async def increment_counter(name: str) -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        # Auto-create on hit
        await db.execute(
            "INSERT INTO counters (name, count) VALUES (?, 1) "
            "ON CONFLICT(name) DO UPDATE SET count = count + 1",
            (name,),
        )
        await db.commit()
    return await get_counter(name)
