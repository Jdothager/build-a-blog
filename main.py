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
import os
import webapp2
import jinja2

from google.appengine.ext import db

# setup jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)


# create class to handle rendering the templates
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


# create Post database
class Post(db.Model):
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


# handles the front page, displaying 5 newest posts
class MainPage(Handler):
    def render_front(self, title="", post="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, post=post, error=error, posts=posts)

    def get(self):
        self.render_front()


# handles new post functions
class NewPost(Handler):
    def render_newpost(self, title="", post="", error=""):
        self.render('newpost.html', title=title, post=post, error=error)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        # error handling
        if not title or not post or (title.strip() == "") or (post.strip() == ""):
            error = "We need both a title and some content!"
            self.render_newpost(title=title, post=post, error=error)
        else:
            a = Post(title=title, post=post)
            a.put()
            self.redirect("/blog/" + str(a.key().id()))


# handles requests to view a single post
class ViewPostHandler(Handler):
    def get(self, id):
        post = Post.get_by_id(int(id))

        if post:
            self.render("singlepost.html", post=post)
        else:
            self.render("blog.html", error="That post ID doesn't exist")


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
