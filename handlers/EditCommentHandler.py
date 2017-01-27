
from google.appengine.ext import db
from handlers.BlogHandler import BlogHandler
from helpers import *

class EditCommentHandler(BlogHandler):

    # def get(self, post_id, post_user_id, comment_id):
    def get(self, post_id, comment_id):

        if not self.user:
            return

        postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
        key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
        comment = db.get(key)
        post = db.get(postKey)

        if not comment:
            return self.redirect('/')

        if not post:
            return self.redirect('/')


        if self.user.key().id() == comment.user_id:

            self.render('editComment.html', content=comment.content, post = post)

        else:
            self.write("You don't have permission to edit this comment.")

    # def post(self, post_id, post_user_id, comment_id):
    def post(self, post_id, comment_id):
        if not self.user:
            return

        postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
        key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
        comment = db.get(key)

        if not comment:
            return self.redirect('/')

        if self.user.key().id() == comment.user_id:
            content = self.request.get('content')

            comment.content = content
            comment.put()

            self.redirect('/' + post_id)

        else:
            self.write("You don't have permission to edit this comment.")
