import sqlite3

con = sqlite3.connect("database.db")

con.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    price INTEGER,
    uid INTEGER REFERENCES users(id)
);
""")

con.commit()
con.close()

print("Database initialized successfully")
