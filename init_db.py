import sqlite3

con = sqlite3.connect("database.db")
con.execute("PRAGMA foreign_keys = ON")

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

con.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);
""")

con.execute("""
CREATE TABLE IF NOT EXISTS item_categories (
    item_id INTEGER,
    category_id INTEGER,
    FOREIGN KEY (item_id) REFERENCES items(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
""")

categories = [
    "Huonekalut",
    "Elektroniikka",
    "Vaatteet",
    "Kengät",
    "Kirjat",
    "Lelut ja pelit",
    "Kodinkoneet",
    "Urheilu ja ulkoilu",
    "Korut ja asusteet",
    "Musiikki ja soittimet"
]

for cat in categories:
    con.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", [cat])

con.commit()
con.close()

print("Database initialized successfully")
