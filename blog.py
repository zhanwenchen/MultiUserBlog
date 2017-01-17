####################################################################
## blog.py
####################################################################
## A blog that allows user profiles, posting, editing, commenting, and liking
## Using the Google Cloud Platform
##
## Author: Zhanwen "Phil" Chen (phil@zhanwenchen.com)
## TODO:
## 1. Add button for new post for logged-in users
## 2. Allow for likes on Posts
## 3. Allow for edits on Posts
## 4. Allow for comments on Posts
## 5. Allow for likes on comments
## 6. Allow for edits on comments
## 7. Add signup in login

import os
import re
import random
import hashlib
import hmac
from string import letters
import webapp2
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

# Helper function to pass everything into jinja templates
def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

####################################################################
## AUTHENTICATION
####################################################################
secret = 'fart'

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

## user password hashing
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_password_hash(name, password, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + password + salt).hexdigest()
    return '%s,%s' % (salt, h)

def validate_password(name, password, h):
    salt = h.split(',')[0]
    return h == make_password_hash(name, password, salt)

####################################################################
## USERS, POSTS and COMMENTS
####################################################################

## User methods and classes

# method to get key????
def users_key(group = 'default'):
    return db.Key.from_path('users', group)

# validate existence and character composition of username
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class User(db.Model):
    name = db.StringProperty(required = True)
    password_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, password, email = None):
        password_hash = make_password_hash(name, password)
        return User(parent = users_key(),
                    name = name,
                    password_hash = password_hash,
                    email = email)

    @classmethod
    def login(cls, name, password):
        u = cls.by_name(name)
        if u and validate_password(name, password, u.password_hash):
            return u


##### blog stuff
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

##### The Post Class is a database
class Post(db.Model):

    ## Specify data attributes for a Post
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    likes = db.IntegerProperty(default=0)
    author = db.StringProperty()
    like_error = db.BooleanProperty(default=False)
    edit_error = db.BooleanProperty(default=False)

    ## Post instance methods
    def render(self):
        ## Local variables to each post
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)

    def incrementLikes(self):
        self.likes += 1
        self.put()

    def toggleLikeError(self):
        if (self.like_error is True):
            self.like_error = False
            self.put()
        else:
            self.like_error = True
            self.put()
    def toggleEditError(self):
        if (self.edit_error is True):
            self.edit_error = False
            self.put()
        else:
            self.edit_error = True
            self.put()
    def deletePost(self):
        self.delete()

class Comment(Post, db.Model):
    post = db.ReferenceProperty(Post, collection_name='comments')

class LikeUsers(db.Model):
    post = db.ReferenceProperty(Post, collection_name='like_users')
    # user = db.ReferenceProperty(User, collection_name='like_users')




####################################################################
## HANDLERS
####################################################################

# Base handler
class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    # Helper function to pass html templates and params to jinja2.
    def render_str(self, template, **params):
        # Add the user object to the params, returns a rendered thing
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

# '/' handler
class MainPage(BlogHandler):
  def get(self):
      self.write('Hello, Udacity!')



class BlogFront(BlogHandler):
    def get(self):
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts = posts)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)

class LikeHandler(BlogHandler):

    def get(self, post_id):
        self.redirect(self.request.referer)

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # Authentication control
        # Prompt user to login before liking
        if (not self.user):
            self.redirect("/login")

        # User likes own post
        elif post.username == self.user.name:
            post.toggleLikeError()
            self.redirect(self.request.referer)
            post.toggleLikeError()
        else:
            post.incrementLikes()
            self.redirect(self.request.referer)
        if not post:
            self.error(404)
            return

class EditHandler(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        # User edits/deletes own post
        if (self.user.name == post.author):
            # render a newpost-like page with pre-populated fields
            self.render("edit.html", p = post, subject=post.subject, content=post.content)

        # User edits/deletes others' post
        else:
            post.toggleEditError()
            self.redirect(self.request.referer)
            post.toggleEditError()

    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        subject = self.request.get('subject')
        content = self.request.get('content')
        # Validate for subject and content
        if subject and content:
            post.subject = subject
            post.content = content
            post.put() # put post back into the db
            self.redirect(self.request.referer) # go to permalink
        # No subject or content
        else:
            error = "subject and content, please!"
            self.render("edit.html", subject=subject, content=content, error=error)

class CommentHandler(BlogHandler):
    pass

class DeleteHandler(BlogHandler):
    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        # User edits/deletes own post
        if (self.user.name == post.author):
            # render a newpost-like page with pre-populated fields
            print '\n\n\n' + str(key) + '\n\n\n'
            post.deletePost()
            self.redirect('/blog')

        # User edits/deletes others' post
        else:
            post.toggleEditError()
            self.redirect(self.request.referer)
            post.toggleEditError()

class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent = blog_key(), subject = subject, content = content, author = self.user.name)
            p.put() # put p into db
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username,
                      email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/blog')

app = webapp2.WSGIApplication([('/', BlogFront),
                               ('/blog/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/([0-9]+)/like', LikeHandler),
                               ('/blog/([0-9]+)/edit', EditHandler),
                               ('/blog/([0-9]+)/delete', DeleteHandler),
                               ('/blog/([0-9]+)/comment', CommentHandler),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
