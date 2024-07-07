from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

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
    recipes = db.relationship('Recipes', backref = 'user', cascade = 'all, delete-orphan', lazy = 'dynamic')
    tricks = db.relationship('Tricks', backref = 'user', cascade = 'all, delete-orphan', lazy = 'dynamic')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields = ('username', 'password')

user_schema = UserSchema()

# Categories table
class Categories(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), unique=True, nullable=False)
    recipes = db.relationship('Recipes', backref = 'category', cascade = 'all, delete-orphan', lazy = 'dynamic')

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
    cat_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    ingredients = db.relationship('Ingredients', backref = 'recipe', cascade = 'all, delete-orphan', lazy = 'dynamic')
    steps = db.relationship('Steps', backref = 'recipe', cascade = 'all, delete-orphan', lazy = 'dynamic')

class RecipeSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'prep_time', 'servings', 'img', 'created_at')

recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)

# Ingredients table
class Ingredients(db.Model):
    __tablename__ = 'ingredient'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

# Steps table
class Steps(db.Model):
    __tablename__ = 'step'
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(100), unique=False, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

# Tricks table
class Tricks(db.Model):
    __tablename__ = 'trick'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=False, nullable=False)
    desc = db.Column(db.String(2000), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.now)
    publish = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = False)
    
class TrickSchema(ma.Schema):
    class Meta:
        fields = ('title', 'desc', 'created_at')

trick_schema = TrickSchema()
tricks_schema = TrickSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)