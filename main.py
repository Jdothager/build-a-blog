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


class Handler(webapp2.RequestHandler):
    """ create class to handle rendering the templates
    """
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Post(db.Model):
    """ create Post database
    """
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
    """ handles the front page, displaying 5 posts
    """
    def render_front(self, title="", post="", error=""):
        # set the page number
        page_str = self.request.get("page")
        if page_str:
            page = int(page_str)
        else:
            page = 1

        # set the offset
        offset = 0
        for each in range(page - 1):
            offset += 5

        # get posts and post count
        posts = get_posts(offset=offset)
        count = posts.count(offset=offset+5)

        # set previous_page and next_page variables
        if page > 1:
            previous_page = page - 1
        else:
            previous_page = False

        if count:
            next_page = page + 1
        else:
            next_page = False

        # render the page
        self.render("blog.html", title=title, post=post, error=error, posts=posts, 
                    previous_page=previous_page, next_page=next_page)

    def get(self):
        self.render_front()


class NewPost(Handler):
    """ handles new post functions
    """
    def render_newpost(self, title="", post="", error_title="", error_post=""):
        self.render('newpost.html', title=title, post=post, error_title=error_title, error_post=error_post)

    def get(self):
        self.render_newpost()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        # error handling
        error_title = ""
        error_post = ""
        if not title or (title.strip() == ""):
            error_title = "Don't forget to add a title!"
        if not post or (post.strip() == ""):
            error_post = "Your post is empty!"
        if error_title or error_post:
            self.render_newpost(title=title, post=post, error_title=error_title, error_post=error_post)
        else:
            a = Post(title=title, post=post)
            a.put()
            self.redirect("/blog/" + str(a.key().id()))


class ViewPostHandler(Handler):
    """ handles requests to view a single post
    """
    def get(self, id):
        post = Post.get_by_id(int(id))

        if post:
            self.render("singlepost.html", post=post)
        else:
            self.render("blog.html", error="That post ID doesn't exist")


def get_posts(limit="5", offset="0"):
    """ filters the database query by count and offset
    """
    posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT " + str(limit) + 
                        "OFFSET " + str(offset))
    return posts


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', MainPage),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
