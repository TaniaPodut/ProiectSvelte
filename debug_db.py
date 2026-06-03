import sqlite3
db_path = 'backend/webtania.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- Tables ---")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print(table[0])

print("\n--- Comanda Table Info ---")
cursor.execute("PRAGMA table_info(comanda)")
for col in cursor.fetchall():
    print(col)

print("\n--- MesajContact Table Info ---")
cursor.execute("PRAGMA table_info(mesajcontact)")
for col in cursor.fetchall():
    print(col)

conn.close()
