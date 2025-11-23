import db

def add_item(title, description, price, uid):
    sql_check = """SELECT id FROM items WHERE title = ? AND description = ? AND price = ? AND uid = ?"""
    existing = db.query(sql_check, [title, description, price, uid])
    if existing:
        return False
    
    sql = """INSERT INTO items (title, description, price, uid)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [title, description, price, uid])
    return True

def get_items():
    sql = """SELECT id, title, description, price, uid FROM items ORDER BY id DESC"""
    result = db.query(sql)
    return result or []

def permission(item_id, uid, action="view"):
    sql = "SELECT uid FROM items WHERE id = ?"
    result = db.query(sql, [item_id])
    if not result:
        return False
    
    owner_id = result[0]["uid"]

    if action == "view":
        return True

    if action in ("edit", "delete"):
        return uid == owner_id
    
    return False

def search_items(keyword):
    sql = """SELECT id, title, description, price, uid
             FROM items
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    return db.query(sql, [f"{keyword}%",f"{keyword}%"])