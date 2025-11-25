CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    price INTEGER,
    uid INTEGER,
    FOREIGN KEY (uid) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS item_categories (
    item_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY(item_id, category_id),
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    uid INTEGER NOT NULL,
    comment TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
    FOREIGN KEY (uid) REFERENCES users(id)
);

INSERT OR IGNORE INTO categories (name) VALUES ('Huonekalut');
INSERT OR IGNORE INTO categories (name) VALUES ('Elektroniikka');
INSERT OR IGNORE INTO categories (name) VALUES ('Vaatteet');
INSERT OR IGNORE INTO categories (name) VALUES ('Kengät');
INSERT OR IGNORE INTO categories (name) VALUES ('Kirjat');
INSERT OR IGNORE INTO categories (name) VALUES ('Lelut ja pelit');
INSERT OR IGNORE INTO categories (name) VALUES ('Kodinkoneet');
INSERT OR IGNORE INTO categories (name) VALUES ('Urheilu ja ulkoilu');
INSERT OR IGNORE INTO categories (name) VALUES ('Korut ja asusteet');
INSERT OR IGNORE INTO categories (name) VALUES ('Musiikki');