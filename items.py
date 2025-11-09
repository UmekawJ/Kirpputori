import db

def add_item(title, description, price, uid):
    sql = """INSERT INTO items (title, description, price, uid)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, price, uid])