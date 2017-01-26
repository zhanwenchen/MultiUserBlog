## User.py
## Zhanwen "Phil" Chen (phil@zhanwenchen.com)
## A class that defines db properties and methods of a User
##

from google.appengine.ext import db
from helpers import *

class User(db.Model):
    name = db.StringProperty(required=True)
    password_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def register(cls, name, password, email=None):
        password_hash = make_password_hash(name, password)
        return User(parent=users_key(),
                    name=name,
                    password_hash=password_hash,
                    email=email)

    @classmethod
    def login(cls, username, password):
        user = User.by_name(username)
        if user and auth_password(username, password, user.password_hash):
            return user

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(cls, name):
        user = User.all().filter('name =', name).get()
        return user
