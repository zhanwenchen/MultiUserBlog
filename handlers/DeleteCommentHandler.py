from google.appengine.ext import db
from handlers.BlogHandler import BlogHandler
from helpers import *

class DeleteCommentHandler(BlogHandler):

    # def get(self, post_id, post_user_id, comment_id):
    def get(self, post_id, comment_id):

        # if self.user and self.user.key().id() == comment.user_id:
        if self.user:
            postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
            key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
            comment = db.get(key)


        elif not self.user:
            self.redirect('/login')

        else:
            self.write("You don't have permission to delete this comment.")

        if self.user.key().id() == comment.user_id:
            comment.delete()
            self.redirect('/' + post_id)
