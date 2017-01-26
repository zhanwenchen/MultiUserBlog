## Comment.py
## Zhanwen "Phil" Chen (phil@zhanwenchen.com)
## A class that defines db properties and methods of a Comment
##

from google.appengine.ext import db

class Comment(db.Model):
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    user_id = db.IntegerProperty(required=True)
    user_name = db.TextProperty(required=True)
