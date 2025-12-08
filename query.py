from db import query

def get_item(item_id):
    return query(
        "SELECT id, title, description, price, uid FROM items WHERE id = ?",
        [item_id]
    )

def get_comments_for_item(item_id):
    return query("""
        SELECT comments.id,
               comments.item_id,
               comments.uid,
               comments.comment,
               comments.created_at,
               users.username
        FROM comments
        JOIN users ON users.id = comments.uid
        WHERE comments.item_id = ?
        ORDER BY comments.created_at DESC
    """, [item_id])
