from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import UserMixin
from flask_login import LoginManager
from flask_security import RoleMixin

login = LoginManager()
db = SQLAlchemy()

     
        
class User(db.Model, UserMixin):
    """Model for the stations table"""
    __tablename__ = 'usernames'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    # gender = db.Column(db.String(150), nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)
    status = db.Column(db.String(150), nullable=False)
    


    def __init__(self, name, email, password,created_on,updated_on,status):
        self.name = name
        self.email = email
        self.status = status
        # self.gender = gender
        self.password_hash = generate_password_hash(password)
        self.created_on = datetime.utcnow()
        self.updated_on = datetime.utcnow()
      

    def check_password(self,  password):
        return check_password_hash(self.password_hash, password)



@login.user_loader
def load_user(id):
    return User.query.get(int(id))