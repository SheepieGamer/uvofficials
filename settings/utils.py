import asqlite

# Database setup
async def setup_database():
    async with asqlite.connect("guilds.db") as db:
        # Create table if it doesn't exist
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guild_info (
                guild_id INTEGER PRIMARY KEY,
                guild_name TEXT,
                modmail_channel_id INTEGER,
                member_role_id INTEGER
            )
        """)
        # Add the column if it doesn't already exist
        try:
            await db.execute("ALTER TABLE guild_info ADD COLUMN member_role_id INTEGER")
        except:
            # Column already exists
            pass
        await db.commit()

# Insert or update guild information
async def upsert_guild_info(guild_id: int, guild_name: str, modmail_channel_id: int, member_role_id: int):
    async with asqlite.connect("guilds.db") as db:
        await db.execute("""
            INSERT INTO guild_info (guild_id, guild_name, modmail_channel_id, member_role_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET
            guild_name=excluded.guild_name, modmail_channel_id=excluded.modmail_channel_id, member_role_id=excluded.member_role_id
        """, (guild_id, guild_name, modmail_channel_id, member_role_id))
        await db.commit()

# Get modmail channel ID by guild ID
async def get_modmail_channel_id(guild_id: int):
    async with asqlite.connect("guilds.db") as db:
        async with db.execute("SELECT modmail_channel_id FROM guild_info WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

# Get member role ID by guild ID
async def get_member_role(guild_id: int):
    async with asqlite.connect("guilds.db") as db:
        async with db.execute("SELECT member_role_id FROM guild_info WHERE guild_id = ?", (guild_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None