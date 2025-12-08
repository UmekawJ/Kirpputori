import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from query import get_item, get_comments_for_item
import config
import db
import items
import secrets
from flask import abort

app = Flask(__name__)
app.secret_key = config.secret_key
@app.route("/")
def index():
    query = request.args.get("query", "").strip()

    categories_list = db.query("SELECT id, name FROM categories ORDER BY name")

    category_items = {}
    for cat in categories_list:
        if query:
            items_in_cat = db.query("""
                SELECT items.id, items.title
                FROM items
                JOIN item_categories ON items.id = item_categories.item_id
                WHERE item_categories.category_id = ?
                  AND (items.title LIKE ? OR items.description LIKE ?)
                ORDER BY items.id DESC
            """, [cat["id"], f"%{query}%", f"%{query}%"])
            
        else:
            items_in_cat = db.query("""
                SELECT items.id, items.title, items.price, items.uid
                FROM items
                JOIN item_categories on items.id = item_categories.item_id
                WHERE item_categories.category_id = ?
                ORDER BY items.id DESC
            """, [cat["id"]])
        
        item_list = []
        for row in items_in_cat:
            item = dict(row)
            count = db.query("SELECT COUNT(*) AS c FROM comments WHERE item_id = ?", [item["id"]])
            item["comment_count"] = count[0]["c"]
            item_list.append(item)

        category_items[cat["name"]] = item_list

    return render_template("index.html", categories=categories_list, category_items=category_items, query=query)

@app.route("/new_item")
def new_item():
    categories = db.query("SELECT id, name FROM categories")
    return render_template("new_item.html", categories=categories)

@app.route("/create_item", methods=["POST"])
def create_item():
    check_csrf()
    if "uid" not in session:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    uid = session["uid"]
    category_id = request.form.get("category")

    items.add_item(title, description, price, uid)
    item_id = db.last_insert_id()

    db.execute("INSERT INTO item_categories (item_id, category_id) VALUES (?, ?)", [item_id, category_id])
    return redirect("/")

@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    uid = session.get("uid")
    if not uid:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    if not items.permission(item_id, uid, "edit"):
        return redirect("/message/Sinula ei ole oikeutta muokata tätä ilmoitusta!")
    
    if request.method == "GET":
        sql = """
            SELECT id, title, description, price, uid
            FROM items
            WHERE id = ?
            """
        result = db.query(sql, [item_id])
        if not result:
            return redirect("/message/Ilmoitusta ei löytynyt")
        item = result[0]
    
        categories = db.query("SELECT id, name FROM categories ORDER BY name")
        selected = db.query("SELECT category_id FROM item_categories WHERE item_id=?", [item_id])
        selected_ids = [s['category_id'] for s in selected]
        
        return render_template("edit_item.html", item=item, categories=categories, selected_ids=selected_ids)
    
    if request.method == "POST":
        check_csrf()
        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        sql= """UPDATE items SET title = ?, description = ?, price = ? WHERE id = ?"""
        db.execute(sql, [title, description, price, item_id])

        db.execute("DELETE FROM item_categories WHERE item_id = ?", [item_id])
        category_id = request.form.get("category")
        if category_id:
            db.execute("INSERT INTO item_categories (item_id, category_id) VALUES(?, ?)", [item_id, category_id])
        return redirect("/message/Ilmoitus päivitetty!")

@app.route("/delete_item/<int:item_id>", methods=["POST", "GET"])
def delete_item(item_id):
    uid = session.get("uid")
    if not uid:
        return redirect("/message/Sinun täytyy kirjautua ensin!")

    item = db.query("SELECT id, title, description, price, uid FROM items WHERE id = ?", [item_id])
    if not item:
        return redirect("/message/Ilmoitusta ei löytynyt")
    item = item[0]

    if not items.permission(item_id, uid, "edit"):
        return redirect("/message/Sinula ei ole oikeutta poistaa tätä ilmoitusta!")
    
    if request.method == "GET":
        return render_template("delete_item.html", item=item)
    
    if request.method == "POST" and "continue" in request.form:
        check_csrf()
        db.execute("DELETE FROM item_categories WHERE item_id = ?", [item_id])
        db.execute("DELETE FROM comments WHERE id = ?", [item_id])
        db.execute("DELETE FROM items WHERE id = ?", [item_id])
        return redirect("/message/Ilmoitus poistettu!")

    return redirect("/")

@app.route("/item/<int:item_id>")
def show_item(item_id):
    item = get_item(item_id)

    if not item:
        return redirect("/message/Ilmoitusta ei löytynyt")
    item = item[0]

    comments = get_comments_for_item(item_id)

    return render_template("item_page.html", item=item, comments=comments)

@app.route("/item/<int:item_id>/comment", methods=["POST"])
def add_comment(item_id):
    check_csrf()
    uid = session.get("uid")
    if not uid:
        return redirect("/login")
    
    comment = request.form.get("comment", "").strip()
    if not comment:
        return redirect(f"/item&{item_id}")
    
    db.execute("INSERT INTO comments (item_id, uid, comment) VALUES (?, ?, ?)", [item_id, uid, comment])

    return redirect(f"/item/{item_id}")

@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    uid = session.get("uid")
    check_csrf()
    if not uid:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    comment = db.query("SELECT id, uid, item_id FROM comments WHERE id = ?", [comment_id])
    if not comment:
        return redirect("/message/Kommenttia ei löytynyt")
    comment = comment[0]

    if comment["uid"] != uid:
        return redirect("/message/Sinulla ei ole oikeutta poistaa tätä kommenttia!")
    
    db.execute("DELETE FROM comments WHERE id = ?", [comment_id])
    return redirect(f"/item/{comment['item_id']}#comments")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return redirect("/message/VIRHE: Salasanat eivät ole samat!")
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return redirect("/message/VIRHE: Tunnus on jo varattu!")
    
    session["uid"] = db.last_insert_id()
    session["username"] = username

    return redirect("/message/Tunnus luotu onnellisesti!")

@app.route("/message/<text>")
def message(text):
    return render_template("message.html", text = text)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])

        if len(result) == 0:
            return render_template("login.html", error="Tunnusta ei löydy")
        
        uid = result[0]["id"]
        password_hash = result[0]["password_hash"]

        if check_password_hash(password_hash, password):
            session["uid"] = uid
            session["username"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Väärin salasana tai tunnus")
        
@app.route("/user/<int:uid>")   
def user_page(uid):
    user = db.query("SELECT id, username FROM users WHERE id = ?", [uid])
    if not user:
        return redirect("/message/Käyttäjää ei löydy")
    user = user[0]

    items = db.query("""
        SELECT 
            items.id,
            items.title,
            items.price,
            items.uid,
            (
                SELECT COUNT(*) 
                FROM comments 
                WHERE comments.item_id = items.id
            ) AS comment_count
        FROM items
        WHERE items.uid = ?
        ORDER BY items.id DESC
    """, [uid])

    item_count = len(items)
    return render_template("user_page.html", user=user, items=items, item_count=item_count)
@app.route("/logout")
def logout():
    session.pop("uid", None)
    session.pop("username", None)
    return redirect("/")

def generate_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)
    return session["csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

def check_csrf():
    token = session.get("csrf_token")
    form_token = request.form.get("csrf_token")

    if not token or not form_token or token != form_token:
        abort(403)
