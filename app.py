from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from sqlalchemy.orm import joinedload

from datetime import datetime

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

# Creating the tables
# UserS table
class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(45), unique=True, nullable=False)
    email = db.Column(db.String(45), unique=True, nullable=False)
    password = db.Column(db.String(45), unique=False, nullable=False)
    recipes = db.relationship('Recipes', backref = 'user_recipes', cascade = 'all, delete-orphan', lazy = 'dynamic')
    tricks = db.relationship('Tricks', backref = 'user_tricks', cascade = 'all, delete-orphan', lazy = 'dynamic')

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
    recipes = db.relationship('Recipes', backref = 'category_recipes', cascade = 'all, delete-orphan', lazy = 'dynamic')

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
    img = db.Column(db.String, unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    publish = db.Column(db.String(20))
    cat_id = db.Column(db.Integer, db.ForeignKey('category_recipes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_recipes.id'), nullable=False)
    user = db.relationship('Users', lazy="joined", innerjoin=True)
    ingredients = db.relationship('Ingredients', backref = 'recipe_ingredients', cascade = 'all, delete-orphan', lazy = 'dynamic')
    steps = db.relationship('Steps', backref = 'recipe_steps', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, title, desc, prep_time, servings, img, publish, cat_id, user_id):
        self.title = title
        self.desc = desc
        self.prep_time = prep_time
        self.servings = servings
        self.img = img
        self.publish = publish
        self.cat_id = cat_id
        self.user_id = user_id

class RecipeSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'prep_time', 'servings', 'img', 'created_at','cat_id','user_id','user.username')
    #    model = models.Recipes
    #    msub_family = fields.Nested("MaterialSubFamiliesSchema")

recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

# Ingredients table
class Ingredients(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe_ingredients.id'), nullable=False)

    def __init__(self, desc, recipe_id):
        self.desc = desc
        self.recipe_id = recipe_id

# Steps table
class Steps(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe_steps.id'), nullable=False)

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
    publish = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user_tricks.id'), nullable = False)
    user = db.relationship('Users', lazy="joined", innerjoin=True)

    def __init__(self, title, desc, publish, cat_id):
        self.title = title
        self.desc = desc
        self.publish = publish
        self.cat_id = cat_id

class TrickSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'created_at','user.username')

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
    cat_name = request.json['cat_name']
    category = Categories.query.filter_by(name = cat_name).first() 

    title = request.json['title']
    desc = request.json['desc']
    prep_time = request.json['prep_time']
    servings = request.json['servings']
    img = request.json['img']
    publish = request.json['publish']
    cat_id = category.id
    user_id = request.json['user_id']

    new_recipe = Recipes(title, desc, prep_time, servings, img, publish, cat_id, user_id)

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
    published_recipes = Recipes.query.options(joinedload(Recipes.user.username, innerjoin=True)).filter_by(publish = "published")
    result = recipes_schema.dump(published_recipes)
    return jsonify(result), {'Access-Control-Allow-Origin':'http://localhost:3000'}

# Endpoint for querying a single recipe
@app.route("/recipe/<id>", methods=["GET"])
def get_recipe(id):
    recipe = Recipes.query.get(id)
    return recipe_schema.jsonify(recipe)



if __name__ == '__main__':
    app.run(debug=True)