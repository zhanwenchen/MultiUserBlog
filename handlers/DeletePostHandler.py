from google.appengine.ext import db
from handlers.BlogHandler import BlogHandler
from helpers import *

class DeletePostHandler(BlogHandler):

    def post(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

        else:
            self.redirect('/login')

        if not post:
            return self.redirect('/')

        if self.user.key().id() == post.user_id:
            post.delete()
            self.redirect('/')

        else:
            comments = db.GqlQuery(
                "select * from Comment where ancestor is :1 order by created desc limit 10", key)

            error = "You don't have permission to delete this post"
            self.render("permalink.html", post=post, comments=comments, error=error)
