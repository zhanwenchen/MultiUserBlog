from google.appengine.ext import db
from handlers.BlogHandler import BlogHandler
from helpers import *
from models.Like import Like

class LikePostHandler(BlogHandler):

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            return self.redirect('/')

        if self.user and self.user.key().id() == post.user_id:
            error = "Sorry, you cannot like your own post."
            # self.redirect(self.request.referer + '/error=' + error)
            # self.render('base.html', error=error)
            # self.response.write(error)
            self.redirect(self.request.referer)
        elif not self.user:
            self.redirect('/login')
        else:
            user_id = self.user.key().id()
            post_id = post.key().id()

            like = Like.all().filter('user_id =', user_id).filter('post_id =', post_id).get()

            # If user already liked the post, unlike it
            if like:
                like.delete()
                post.likes -= 1
                post.put()
                self.redirect(self.request.referer)

            else:
                like = Like(parent=key,
                            user_id=self.user.key().id(),
                            post_id=post.key().id())

                post.likes += 1

                like.put()
                post.put()

                self.redirect(self.request.referer)
