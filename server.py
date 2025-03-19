from flask import Flask, session, Response, request, redirect, url_for, render_template
import data_model as model
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

global user_data
username = "testuser"
password = "hello123"
password_hash = generate_password_hash(password)
user_data = {"User": {"views": 0, "password_hash": password_hash}}


app = Flask(__name__)


app.secret_key = b"ec68a703c4a06b435b5654c34da1d8c6ae35ffcf060c7d70a6ab4f9cec2f2025"


########################################
# Routes des pages principales du site #
########################################


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not ("username" in session):
            return Response("Acces Denied, you have to login", status=401)
        else:
            return f(*args, **kwargs)

    return decorated_function


@app.get("/login")
def login_form():
    return render_template("login.html")


@app.post("/login")
def verify_login():
    username = request.form["username"]
    password = request.form["password"]
    error = None
    if not (username in user_data):
        error = "Nom d'utilisateur incorrect"
    else:
        password_hash = user_data[username]["password_hash"]
        if not (check_password_hash(password_hash, password)):
            error = "Mot de passe incorrect"
    if error is None:
        session.clear()
        session["username"] = username
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login_form"))


@app.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# Retourne une page principale avec le nombre de recettes
@app.get("/")
def home():
    if "username" in session:
        username = session["username"]
        user_data[username]["views"] = user_data[username]["views"] + 1
        return render_template(
            "index.html",
            logged_in=True,
            username=username,
            views=user_data[username]["views"],
        )
    else:
        return render_template("index.html", logged_in=False, username=None, views=None)


@app.get("/new_user")
def new_user_form():
    return render_template("new_user.html")


@app.post("/new_user")
def add_new_user():
    username = request.form["username"]
    password = request.form["password"]
    password_hash = generate_password_hash(password)

    user_id = model.new_user(name, password)

    session.clear()
    session["username"] = name
    return redirect(url_for("home"))


# Retourne les résultats de la recherche à partir de la requête "query"
@app.get("/search")
def search():
    if "page" in request.args:
        page = int(request.args["page"])
    else:
        page = 1
    if "query" in request.args:
        query = request.args["query"]
    else:
        query = ""
    found = model.search(query, page)
    return render_template("search.html", found=found)


# Retourne le contenu d'une recette d'identifiant "id"
@app.get("/read/<id>")
def read(id):
    recipe = model.read(int(id))
    return render_template("read.html", recipe=recipe)


@app.get("/create")
@login_required
def create_form():
    return render_template("create.html")


@app.get("/update/<id>")
@login_required
def update_form(id):
    recipe = model.read(int(id))
    return render_template("update.html", recipe=recipe)


@app.get("/delete/<id>")
@login_required
def delete_form(id):
    entry = model.read(int(id))
    return render_template("delete.html", id=id, title=entry["title"])


############################################
# Routes pour modifier les données du site #
############################################


def parse_user_list(user_list):
    l = user_list.strip().split("-")
    l = [e.strip() for e in l]
    l = [e for e in l if len(e) > 0]
    return l


# Fonction qui facilite la création d'une recette
def post_data_to_recipe(form_data):
    ingredients = parse_user_list(form_data["ingredients"])
    stages = parse_user_list(form_data["stages"])
    return {
        "title": form_data["title"],
        "description": form_data["description"],
        "img": form_data["img"],
        "duration": form_data["duration"],
        "ingredients": ingredients,
        "stages": stages,
    }


@app.post("/create")
def create_post():
    id = model.create(post_data_to_recipe(request.form))
    return redirect(url_for("read", id=str(id)))


@app.post("/update/<id>")
def update_post(id):
    id = int(id)
    model.update(id, post_data_to_recipe(request.form))
    return redirect(url_for("read", id=str(id)))


@app.post("/delete/<id>")
def delete_post(id):
    model.delete(int(id))
    return redirect(url_for("home"))
