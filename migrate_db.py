import sqlite3
import datetime

db_path = 'backend/webtania.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing columns
cursor.execute('PRAGMA table_info(comanda)')
columns = [row[1] for row in cursor.fetchall()]

if 'status' not in columns:
    print("Adding 'status' column to 'comanda' table...")
    cursor.execute("ALTER TABLE comanda ADD COLUMN status TEXT DEFAULT 'pending'")

if 'created_at' not in columns:
    print("Adding 'created_at' column to 'comanda' table...")
    cursor.execute("ALTER TABLE comanda ADD COLUMN created_at DATETIME")
    # Update existing rows with current time
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("UPDATE comanda SET created_at = ?", (now,))

# Fix mesajcontact table
cursor.execute('PRAGMA table_info(mesajcontact)')
columns_msg = [row[1] for row in cursor.fetchall()]

if 'created_at' not in columns_msg:
    print("Adding 'created_at' column to 'mesajcontact' table...")
    cursor.execute("ALTER TABLE mesajcontact ADD COLUMN created_at DATETIME")
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    cursor.execute("UPDATE mesajcontact SET created_at = ?", (now,))

conn.commit()
conn.close()
print("Migration completed.")
