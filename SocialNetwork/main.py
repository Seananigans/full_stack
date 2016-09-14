import os
import random
import time

import webapp2
import jinja2

from security_features import *
from validation import *
from db_setup import *


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


"""HANDLERS FOR WEBPAGES"""
class Handler(webapp2.RequestHandler):
	"""Creates basic functionality for all pages."""
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def set_secure_cookie(self, name, val):
		cookie_val = str( make_secure_val(val) )
		self.response.headers.add_header(
			'Set-Cookie',
			'%s=%s; Path=/' % (name, cookie_val))

	def read_secure_cookie(self, name):
		cookie_val = self.request.cookies.get(name)
		return cookie_val and check_secure_val(cookie_val)

	def login(self, user):
		self.set_secure_cookie("username", str(user.key().id()))

	def logout(self):
		self.response.headers.add_header('Set-Cookie', 'username=; Path=/')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('username')
		self.user = uid and User.by_id(int(uid))

class SignUp(Handler):
	"""Handles requests to create a user in the system"""
	def render_front(self, username="", email=""):
		self.render("signup.html", username=username, email=email)

	def get(self):
		username=""
		username_cookie_str = self.request.cookies.get(username)
		if username_cookie_str:
			username_cookie_val = check_secure_val(username_cookie_str)
			if username_cookie_val:
				username = username_cookie_val

		self.render_front()

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")

		needs_username = not valid_username(username)
		needs_password = not valid_password(password)
		needs_verify = (password != verify)
		needs_email = not valid_email(email)

		if needs_verify or needs_username or needs_password or needs_email:
			error = "Please properly fill in all required fields."
			self.render("signup.html",
				username=username,
				email=email,
				needs_username = needs_username,
				needs_password = needs_password,
				needs_verify = needs_verify,
				needs_email = needs_email,
				error=error)
		else:
			user = User.by_name(name=username)
			if user:
				error = "Username exists. Please pick a different Username."
				self.render("signup.html",
					username=username,
					email=email,
					needs_username = needs_username,
					needs_password = needs_password,
					needs_verify = needs_verify,
					needs_email = needs_email,
					error=error)
			else:
				u = User.register(name=username, password=password, email=email)
				u.put()
				self.login(u)
				self.redirect("/welcome")

class Login(Handler):
	"""Handles requests to log a user into the system"""
	def render_front(self, username="", error=""):
		self.render("login.html", username=username, error=error)

	def get(self):
		self.render_front()

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")

		if not (valid_username(username) and valid_password(password)):
			error = "Please enter a valid username and password."
			self.render_front(username=username, error=error)
		else:
			user = User.login(name=username, password=password)
			if user:
				self.login(user)
				self.redirect("/welcome")
			else:
				error = "The username and password do not match."
				self.render_front(username=username, error=error)

class Logout(Handler):
	"""Handles requests to log a user out of the system"""
	def get(self):
		self.logout()
		self.redirect("/login")

class Welcome(Handler):
	"""Handles requests to render the welcome/front page."""
	def get(self):
		username = self.read_secure_cookie("username")
		if self.user:
			posts = Post.by_created()
			self.render('welcome.html', username=self.user.name, posts=posts)
		else:
			self.redirect("/signup")

class NewPost(Handler):
	"""Handles requests to render the new post page and create a post."""
	def render_front(self, error=""):
		self.render("newPost.html", name=self.user.name, error=error)

	def get(self):
		if self.user:
			self.render_front()
		else:
			self.redirect('/login')

	def post(self):
		user = self.user.name
		post = self.request.get("post")
		if post and len(post.strip())>0:
			post = Post(name=user, entry=post)
			post.put()
			time.sleep(0.1)
			self.redirect("/welcome")
		else:
			error = "Please enter some text for the post."
			self.render_front(error=error)

class EditPost(Handler):
	"""Handles requests to render the edit post page and edit a post."""
	def render_front(self, post=None, error=""):
		self.render("editPost.html", name=self.user.name, post=post, error=error)

	def get(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)

		if self.user and self.user.name==post.name:
			self.render_front(post=post)
		else:
			self.redirect('/login')

	def post(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)
		user = self.user.name
		changed_post = self.request.get("post")

		if self.user and post and self.user.name==post.name:
			if changed_post and len(changed_post.strip())>0:
				post.entry = changed_post
				post.put()
				time.sleep(0.1)
				self.redirect("/welcome")
			else:
				error = "Please enter some text for the post."
				self.render_front(post=post, error=error)

class DeletePost(Handler):
	"""Handles requests to render the delete post page and delete a post."""
	def render_front(self, post=None):
		self.render("deletePost.html", name=self.user.name, post=post)

	def get(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)

		if not post:
			self.error(404)
			return
		else:
			if self.user and self.user.name==post.name:
				self.render_front(post)
			else:
				self.redirect('/login')

	def post(self, post_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)

		user = self.user.name

		if self.user and self.user.name==post.name:
			post.delete()
			time.sleep(0.1)
			self.redirect('/welcome')
		else:
			self.redirect('/login')

class NewComment(Handler):
	"""Handles requests to render the new comments page and create comments."""
	def render_front(self, post=None, error=""):
		self.render("newComment.html", name=self.user.name, post=post, error=error)

	def get(self, post_id):
		if self.user:
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)
			self.render_front(post=post)
		else:
			self.redirect('/login')

	def post(self, post_id):
		if self.user:
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)

			content = self.request.get("comment")
			if content:
				author = self.user.name
				post_id = post_id

				comment = Comment(
					author=author,
					content=content,
					post_id=post_id)
				comment.put()
				time.sleep(0.1)
				self.redirect('/welcome')
			else:
				error = "Please enter some text for the comment."
				self.render_front(post=post, error=error)
		else:
			self.redirect('/login')

class EditComment(Handler):
	"""Handles requests to render the edit comments page and edit comments for a post."""
	def render_front(self, post=None, comment=None, error=""):
		self.render("editComment.html", name=self.user.name, post=post, comment=comment, error=error)

	def get(self, post_id, comment_id):
		if self.user:
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)

			ckey = db.Key.from_path("Comment", int(comment_id))
			comment = db.get(ckey)

			self.render_front(post=post, comment=comment)
		else:
			self.redirect('/login')

	def post(self, post_id, comment_id):
		if self.user:
			content = self.request.get("comment")

			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)

			ckey = db.Key.from_path("Comment", int(comment_id))
			comment = db.get(ckey)

			if self.user.name==comment.author:
				if content:
					comment.content = content
					comment.put()
					time.sleep(0.1)
					self.redirect('/welcome')
				else:
					error = "Please enter some text for the comment."
					self.render_front(post=post, comment=comment, error=error)
			else:
				self.redirect('/welcome')

		else:
			self.redirect('/login')



class DeleteComment(Handler):
	"""Handles requests to render the delete comments page and edit comments for a post."""
	def render_front(self, post=None, comment=None):
		self.render("deleteComment.html", post=post, comment=comment)

	def get(self, post_id, comment_id):
		key = db.Key.from_path("Post", int(post_id))
		post = db.get(key)

		ckey = db.Key.from_path("Comment", int(comment_id))
		comment = db.get(ckey)

		self.render_front(post=post, comment=comment)

	def post(self, post_id, comment_id):
		if self.user:
			content = self.request.get("comment")

			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)

			ckey = db.Key.from_path("Comment", int(comment_id))
			comment = db.get(ckey)

			if self.user.name==comment.author:
				comment.delete()
				time.sleep(0.1)
				self.redirect('/welcome')
			else:
				self.redirect('/welcome')

		else:
			self.redirect('/login')

class LikePost(Handler):
	"""Handles requests to like posts."""
	def get(self, post_id):
		if self.user:
			key = db.Key.from_path("Post", int(post_id))
			post = db.get(key)

			if post.name != self.user.name:
				like = Likes.all().filter("post_id =", post_id).filter("author =", self.user.name).get()
				if like:
					like.delete()
				else:
					like = Likes(author=self.user.name, post_id=post_id)
					like.put()
				time.sleep(0.1)
			self.redirect('/welcome')
		else:
			self.redirect('/login')


app = webapp2.WSGIApplication([
	("/", Welcome),
	("/welcome", Welcome),
	("/signup", SignUp),
	("/login", Login),
	("/logout", Logout),
	("/new", NewPost),
	("/like/(\d+)", LikePost),
	("/edit/(\d+)", EditPost),
	("/delete/(\d+)", DeletePost),
	("/newcomment/(\d+)", NewComment),
	("/edit/(\d+)/editcomment/(\d+)", EditComment),
	("/delete/(\d+)/deletecomment/(\d+)", DeleteComment)
	], debug=True)