from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS, cross_origin
import os

from datetime import datetime

app = Flask(__name__)
CORS(app, support_credentials=True)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app, session_options={"autoflush": False})
ma = Marshmallow(app)

# Creating the tables
# UserS table
class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(45), unique=False, nullable=False)
    recipe = db.relationship('Recipes', backref = 'user_recipe', cascade = 'all, delete-orphan', lazy = 'dynamic')
    trick = db.relationship('Tricks', backref = 'user_trick', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')

user_schema = UserSchema()
users_schema = UserSchema(many=True)

# Categories table
class Categories(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    recipe = db.relationship('Recipes', backref = 'category_recipe', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, name):
        self.name = name

class CategorySchema(ma.Schema):
    class Meta:
        fields = ('id','name',)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)
        
# Recipes table
class Recipes(db.Model):
    __tablename__ = 'recipe'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    desc = db.Column(db.String(500), unique=False, nullable=True)
    prep_time = db.Column(db.String(45), unique=False, nullable=False)
    servings = db.Column(db.Integer, unique=False, nullable=False)
    img = db.Column(db.BLOB, unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    published_on = db.Column(db.DateTime, nullable=True)
    publish_status = db.Column(db.String(20))
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ingredient = db.relationship('Ingredients', backref = 'recipe_ingredient', cascade = 'all, delete-orphan', lazy = 'dynamic')
    step = db.relationship('Steps', backref = 'recipe_step', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, title, desc, prep_time, servings, img, published_on, publish_status, cat_id, user_id):
        self.title = title
        self.desc = desc
        self.prep_time = prep_time
        self.servings = servings
        self.img = img
        self.publish_status = publish_status
        self.published_on = published_on
        self.cat_id = cat_id
        self.user_id = user_id

class RecipeSchema(ma.Schema):
    class Meta:
        fields = ('id','title', 'desc', 'prep_time', 'servings', 'img', 'published_on','cat_id','user_id','username')

recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

# Ingredients table
class Ingredients(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __init__(self, desc, recipe_id):
        self.desc = desc
        self.recipe_id = recipe_id

# Steps table
class Steps(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

    def __init__(self, desc, recipe_id):
        self.desc = desc
        self.recipe_id = recipe_id

# Tricks table
class Tricks(db.Model):
    __tablename__ = 'trick'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    desc = db.Column(db.String(2000), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    published_on = db.Column(db.DateTime, nullable=True)
    publish_status = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)

    def __init__(self, title, desc, published_on, publish_status, user_id):
        self.title = title
        self.desc = desc
        self.published_on = published_on
        self.publish_status = publish_status
        self.user_id = user_id

class TrickSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'published_on', 'user_id', 'user.username')

trick_schema = TrickSchema()
tricks_schema = TrickSchema(many=True)

#Endpoint to register an user
"""@app.post("/register")
def register(user: User):
    # Check if user already exists in the database
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        return {"message": "User already exists"}
    # Insert the new user into the database
    user_dict = user.dict()
    users_collection.insert_one(user_dict)
    # Generate a token
    token = generate_token(user.email)
    # Convert ObjectId to string
    user_dict["_id"] = str(user_dict["_id"])
    # Store user details and token in local storage
    user_dict["token"] = token
    return user_dict"""

# Endpoint to create a new user
@app.route('/user', methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    new_user = Users(username, email, password)

    db.session.add(new_user)
    db.session.commit()

    user = Users.query.get(new_user.id)

    return user_schema.jsonify(user)

# Endpoint to create a new category
@app.route('/category', methods=["POST"])
def add_category():
    name = request.json['name']

    new_category = Categories(name)

    db.session.add(new_category)
    db.session.commit()

    category = Categories.query.get(new_category.id)

    return category_schema.jsonify(category)

# Endpoint to query all categories
@app.route("/categories", methods=["GET"])
def get_categories():
    all_categories = Categories.query.all()
    result = categories_schema.dump(all_categories)
    return jsonify(result)

# Endpoint for querying a single category
@app.route("/category/<id>", methods=["GET"])
def get_category(id):
    category = Categories.query.get(id)
    return category_schema.jsonify(category)

# Endpoint for updating a category
@app.route("/category/<id>", methods=["PUT"])
def update_category(id):
    category = Categories.query.get(id)
    name = request.json['name']

    category.name = name

    db.session.commit()
    return category_schema.jsonify(category)

# Endpoint to delete a category
@app.route("/category/<id>", methods=["DELETE"])
def delete_category(id):
    category = Categories.query.get(id)
    db.session.delete(category)
    db.session.commit()
    return "Category was successfully deleted"

# Endpoint to create a new recipe
@app.route('/recipe', methods=["POST"])
def add_recipe():
    print("File sent:", request.files['img'])
    cat_name = request.form['cat_name']
    category = Categories.query.filter_by(name = cat_name).first() 

    print("Category id:", category.id)

    title = request.form['title']
    desc = request.form['desc']
    prep_time = request.form['prep_time']
    servings = request.form['servings']
    img = request.files['img'].read()
    published_on = request.form['published_on']
    publish_status = request.form['publish_status']
    cat_id = category.id
    user_id = request.form['user_id']

    new_recipe = Recipes(title, desc, prep_time, servings, img, published_on, publish_status, cat_id, user_id)

    db.session.add(new_recipe)
    recipe = Recipes.query.get(new_recipe.id)
    
    ingredients = request.json['ingredients']
    for ingredient in ingredients:
        desc = ingredient
        recipe_id = new_recipe.id
        
        new_ingredient = Ingredients(desc, recipe_id)
        
        db.session.add(new_ingredient)

    steps = request.json['steps']
    for step in steps:
        desc = step
        recipe_id = new_recipe.id
        
        new_step = Steps(desc, recipe_id)
        
        db.session.add(new_step) 

    db.session.commit()

    return recipe_schema.jsonify(recipe)

# Endpoint to get all the published recipes
@app.route("/recipes", methods=["GET"])
def get_recipes():
    results = db.session.query(Recipes.id, Recipes.title, Recipes.desc, Recipes.prep_time, Recipes.servings, Recipes.img, Recipes.created_at, Recipes.cat_id, Recipes.user_id, Users.username).\
    join(Users, Recipes.user_id == Users.id).\
    filter(Recipes.publish_status == 'published').\
    order_by(Recipes.created_at.desc())
    

    published_recipes = recipes_schema.dump(results)

    return jsonify(published_recipes), {'Access-Control-Allow-Origin':'http://localhost:3000'}

# Endpoint to get all the published recipes of a given category
@app.route("/recipes/<cat>", methods=["GET"])
def get_recipes_by_cat(cat):
    results = db.session.query(Recipes.id, Recipes.title, Recipes.desc, Recipes.prep_time, Recipes.servings, Recipes.img, Recipes.created_at, Recipes.cat_id, Recipes.user_id, Users.username).\
    join(Users, Recipes.user_id == Users.id).\
    filter(Recipes.publish_status == 'published', Recipes.cat_id == cat).\
    order_by(Recipes.created_at.desc())

    published_recipes_by_cat = recipes_schema.dump(results)

    return jsonify(published_recipes_by_cat), {'Access-Control-Allow-Origin':'http://localhost:3000'}

# Endpoint for querying a single recipe
@app.route("/recipe/<id>", methods=["GET"])
def get_recipe(id):

    recipe = db.session.query(Recipes.id, Recipes.title, Recipes.desc, Recipes.prep_time, Recipes.servings, Recipes.img, Recipes.created_at, Recipes.cat_id, Recipes.user_id, Users.username).\
    join(Users, Recipes.user_id == Users.id).\
    filter(Recipes.id == id).\
    first()
    
    q_ingredients = db.session.query(Ingredients).filter(Ingredients.recipe_id == id).all()

    ingredients = []
    for ingredient in q_ingredients:
        ingredients.append(ingredient.desc)

    q_steps = db.session.query(Steps).filter(Steps.recipe_id == id).all()
    
    steps = []
    for step in q_steps:
        steps.append(step.desc)

    complete_recipe = {
        "id": recipe[0],
        "title": recipe[1],
        "desc": recipe[2],
        "prep_time": recipe[3],
        "servings": recipe[4],
        "img": recipe[5],
        "created_at": recipe[6],
        "cat_id": recipe[7],
        "user_id": recipe[8],
        "username": recipe[9],
        "ingredients": ingredients,
        "steps": steps
    }

    return complete_recipe, {'Access-Control-Allow-Origin':'http://localhost:3000'}

# Endpoint to delete a recipe
@app.route("/recipe/<id>", methods=["DELETE"])
@cross_origin(supports_credentials=True)
def delete_recipe(id):
    recipe = Recipes.query.get(id)
    db.session.delete(recipe)
    db.session.commit()
    return "Recipe was successfully deleted"

# Endpoint to create a new cooking trick
@app.route('/trick', methods=["POST"])
def add_trick():
    
    title = request.json['title']
    desc = request.json['desc']
    publish_status = request.json['publish_status']
    user_id = request.json['user_id']

    new_trick = Tricks(title, desc, publish_status, user_id)

    db.session.add(new_trick)
    trick = Tricks.query.get(new_trick.id)

    db.session.commit()

    return trick_schema.jsonify(trick)

# Endpoint to get all the published cooking tricks
@app.route("/tricks", methods=["GET"])
def get_tricks():
    results = db.session.query(Tricks.id, Tricks.title, Tricks.desc, Tricks.created_at, Tricks.user_id, Users.username).\
    join(Users, Tricks.user_id == Users.id).\
    filter(Tricks.publish_status == 'published').\
    order_by(Tricks.created_at.desc())
    

    published_recipes = recipes_schema.dump(results)

    return jsonify(published_recipes), {'Access-Control-Allow-Origin':'http://localhost:3000'}

if __name__ == '__main__':
    app.run(debug=True)