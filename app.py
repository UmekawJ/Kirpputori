import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import config
import db
import items

app = Flask(__name__)
app.secret_key = config.secret_key
@app.route("/")
def index():
    all_items = items.get_items()
    return render_template("index.html", items=all_items)

@app.route("/new_item")
def new_item():
    return render_template("new_item.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    if "uid" not in session:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    title = request.form["title"]
    description = request.form["description"]
    price = request.form["price"]
    uid = session["uid"]

    items.add_item(title, description, price, uid)
    return redirect("/")

@app.route("/edit_item/<int:item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    uid = session.get("uid")
    if not uid:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    if not items.permission(item_id, uid, "edit"):
        return redirect("/message/Sinula ei ole oikeutta muokata tätä ilmoitusta!")
    
    if request.method == "GET":
        sql = "SELECT * FROM items WHERE id = ?"
        result = db.query(sql, [item_id])
        if not result:
            return redirect("/message/Ilmoitusta ei löytynyt")
        return render_template("edit_item.html", item=result[0])
    
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        price = request.form["price"]
        sql= """UPDATE items SET title = ?, description = ?, price = ? WHERE id = ?"""
        db.execute(sql, [title, description, price, item_id])
        return redirect("/message/Ilmoitus päivitetty!")

@app.route("/delete_item/<int:item_id>", methods=["POST", "GET"])
def delete_item(item_id):
    uid = session.get("uid")
    if not uid:
        return redirect("/message/Sinun täytyy kirjautua ensin!")
    
    item = db.query("SELECT * FROM items WHERE id = ?", [item_id])
    if not item:
        return redirect("/message/Ilmoitusta ei löytynyt")
    item = item[0]
    
    if not items.permission(item_id, uid, "edit"):
        return redirect("/message/Sinula ei ole oikeutta poistaa tätä ilmoitusta!")
    
    if request.method == "GET":
        return render_template("delete_item.html", item=item)
    
    if "continue" in request.form:
        db.execute("DELETE FROM items WHERE id = ?", [item_id])
        return redirect("/message/Ilmoitus poistettu!")
    
    return redirect("/")

    
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
            return redirect("/message/Tunnusta ei löydy")
        
        uid = result[0]["id"]
        password_hash = result[0]["password_hash"]

        if check_password_hash(password_hash, password):
            session["uid"] = uid
            session["username"] = username
            return redirect("/")
        else:
            return redirect("/message/Väärin salasana tai tunnus")

@app.route("/logout")
def logout():
    session.pop("uid", None)
    session.pop("username", None)
    return redirect("/")