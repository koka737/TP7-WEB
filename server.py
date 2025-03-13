from flask import Flask, session, Response, request, redirect, url_for, render_template
import data_model as model

app = Flask(__name__)


########################################
# Routes des pages principales du site #
########################################

# Retourne une page principale avec le nombre de recettes
@app.get('/')
def home():
  return render_template('index.html')


# Retourne les résultats de la recherche à partir de la requête "query"
@app.get('/search')
def search():
  if 'page' in request.args:
    page = int(request.args["page"])
  else:
    page = 1
  if 'query' in request.args:
    query = request.args["query"]
  else:
    query = ""
  found = model.search(query, page)
  return render_template('search.html', found=found)

# Retourne le contenu d'une recette d'identifiant "id"
@app.get('/read/<id>')
def read(id):
  recipe = model.read(int(id))
  return render_template('read.html', recipe=recipe)


@app.get('/create')
def create_form():
  return render_template('create.html')

@app.get('/update/<id>')
def update_form(id):
  recipe = model.read(int(id))
  return render_template('update.html', recipe=recipe)


@app.get('/delete/<id>')
def delete_form(id):
  entry = model.read(int(id))
  return render_template('delete.html', id=id, title=entry['title'])


############################################
# Routes pour modifier les données du site #
############################################


def parse_user_list(user_list):
  l = user_list.strip().split("-")
  l = [e.strip() for e in l]
  l = [e for e in l if len(e)> 0]
  return l
# Fonction qui facilite la création d'une recette
def post_data_to_recipe(form_data):
  ingredients = parse_user_list(form_data['ingredients'])
  stages = parse_user_list(form_data['stages'])
  return {
    'title': form_data['title'], 
    'description': form_data['description'],
    'img': form_data['img'],
    'duration': form_data['duration'],
    'ingredients': ingredients,
    'stages': stages
  }

@app.post('/create')
def create_post():
  id = model.create(post_data_to_recipe(request.form))
  return redirect(url_for('read', id=str(id)))


@app.post('/update/<id>')
def update_post(id):
  id = int(id)
  model.update(id, post_data_to_recipe(request.form))
  return redirect(url_for('read', id=str(id)))


@app.post('/delete/<id>')
def delete_post(id):
  model.delete(int(id))
  return redirect(url_for('home'))
