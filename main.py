####################################################################
## blog.py
####################################################################
## A blog that allows user profiles, posting, editing, commenting, and liking
## Using the Google Cloud Platform
##
## Author: Zhanwen "Phil" Chen (phil@zhanwenchen.com)
##
## Instructions:
## 1. In project directory
##      $ dev_appserver.py app.yaml
## 2. To clear all existing database
##      $ dev_appserver.py --clear_datastore=yes app.yaml
##
##
##
##
## TODO:
## 1. Add button for new post for logged-in users
## 2. Allow for likes on Posts
##
## Post must update its own likes.
##
## 1. query likes.
##  But given that Post is itself a db,
##  how does it call another db (Like)?
##
## 2. increment likes
##  Brittle, but whatever let's do that now.
##
##
## 3. Allow for edits on Posts
## 4. Allow for comments on Posts
## 5. Allow for likes on comments
## 6. Allow for edits on comments
## 7. Add signup in login
##
## Known Issues:
## 1. Redirect/Referer Error for likes


#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# General
from webapp2 import WSGIApplication
from google.appengine.ext import db
from helpers import *


# Models
from models.User import User
from models.Post import Post
from models.Like import Like
from models.Comment import Comment


# Handlers

from handlers.BlogHandler import BlogHandler
from handlers.BlogFrontHandler import BlogFrontHandler
from handlers.SignupHandler import SignupHandler
from handlers.LoginHandler import LoginHandler
from handlers.LogoutHandler import LogoutHandler
from handlers.PostHandler import PostHandler
from handlers.NewPostHandler import NewPostHandler
from handlers.EditPostHandler import EditPostHandler
from handlers.DeletePostHandler import DeletePostHandler
from handlers.LikePostHandler import LikePostHandler
from handlers.NewCommentHandler import NewCommentHandler
from handlers.EditCommentHandler import EditCommentHandler
from handlers.DeleteCommentHandler import DeleteCommentHandler


# Routing
app = WSGIApplication([
    ('/', BlogFrontHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', PostHandler),
    ('/([0-9]+)/like', LikePostHandler),
    ('/([0-9]+)/edit', EditPostHandler),
    ('/([0-9]+)/delete', DeletePostHandler),
    ('/([0-9]+)/comment', NewCommentHandler),
    ('/([0-9]+)/editcomment/([0-9]+)', EditCommentHandler),
    # ('/([0-9]+)/([0-9]+)/editcomment/([0-9]+)', EditCommentHandler),
    # ('/([0-9]+)/([0-9]+)/deletecomment/([0-9]+)', DeleteCommentHandler)
    ('/([0-9]+)/deletecomment/([0-9]+)', DeleteCommentHandler)
], debug=True)
