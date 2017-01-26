from google.appengine.ext import db
from handlers.BlogHandler import BlogHandler
from helpers import *
from models.Comment import Comment

class NewCommentHandler(BlogHandler):

    def get(self, post_id):

        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            self.render('newComment.html', post=post)

        else:
            self.redirect('/login')

    def post(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            # post = db.get(key)

            content = self.request.get('content')

            comment = Comment(parent=key, user_id=self.user.key().id(), content=content, user_name=self.user.name)
            comment.put()

            self.redirect('/' + post_id)

        else:
            self.redirect('/login')
