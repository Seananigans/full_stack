import os
import time

import jinja2
import webapp2
import re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

from google.appengine.ext import db


def encrypt(string, enc=13):
	alphabet = "abcdefghijklmnopqrstuvwxyz"

	encrypted = ""
	for letter in string:
		lower_search = letter.lower()
		if lower_search in alphabet:
			idx = (alphabet.index(lower_search) + enc)%26
			if letter.isupper():
				encrypted += alphabet[idx].upper()
			else:
				encrypted += alphabet[idx]
		else:
			encrypted += letter
	return encrypted

def validate_email(email):
	if "@" in email:
		return True
	else:
		return False

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(username):
    return USER_RE.match(username)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
	return not email or EMAIL_RE.match(email)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		self.render("base.html")

class DecryptHandler(Handler):
	def get(self):
		self.render("encryption.html")
	def post(self):
		t = self.request.get("text")
		new_t = encrypt(string=t)
		self.render("encryption.html", text=new_t)

class SignUpHandler(Handler):
	def get(self):
		self.render("signup.html")

	def post(self):
		user_name = self.request.get("username")
		password = self.request.get("password")
		verify_password = self.request.get("verify_password")
		email = self.request.get("email")

		needs_username = not valid_username(user_name)
		needs_password = not valid_password(password)
		unverified = (password!=verify_password)
		needs_email = not valid_email(email)

		if unverified or needs_password or needs_username or needs_email:
			self.render("signup.html", 
				username=user_name,
				email=email,
				needs_username=needs_username, 
				needs_password=needs_password,
				unverified=unverified, 
				needs_email=needs_email)
		else:
			self.redirect("/welcome?username="+user_name)

class AcceptanceHandler(Handler):
	def get(self):
		username = self.request.get("username")
		if valid_username(username):
			self.render("acceptance.html", username=username)
		else:
			self.redirect("/signup")

class Art(db.Model):
	title = db.StringProperty(required=True)
	art = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)


class ASCIIHandler(Handler):
	def render_front(self, title="", art="", error=""):
		arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 5")
		self.render("ascii_front.html", title=title, art=art, error=error, arts=arts)

	def get(self):
		self.render_front()

	def post(self):
		title = self.request.get("title")
		art = self.request.get("art")

		if title and art:
			a = Art(title=title, art=art)
			a.put()
			time.sleep(0.1)
			self.redirect("/ascii")
		else:
			error = "we need both values to make a post."
			self.render_front(title=title, art=art, error=error)

###################################################################################################
class BlogHandler(Handler):
	def render_front(self):
		posters = db.GqlQuery("SELECT * FROM Poster ORDER BY created DESC LIMIT 10")
		self.render("blog.html", posters=posters)

	def get(self):
		self.render_front()

class OldPostHandler(Handler):
	def get(self, poster_id):
		poster = Poster.get_by_id(int(poster_id))

		self.render("blog.html", posters=[poster])

class Poster(db.Model):
	subject = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class NewPostHandler(Handler):
	def render_front(self, subject="", content="", error=""):
		self.render("newpost.html", subject=subject, content=content, error=error)

	def get(self):
		self.render_front()

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")

		if subject and content:
			e = Poster(subject=subject, content=content)
			e.put()
			time.sleep(0.1)
			self.redirect("/blog/%d" % e.key().id())
		else:
			error = "we need both values to make a poster."
			self.render_front(subject=subject, content=content, error=error)

app = webapp2.WSGIApplication([
	("/rot13", DecryptHandler), 
	("/signup", SignUpHandler),
	("/welcome", AcceptanceHandler),
	("/blog", BlogHandler),
	("/blog/newpost", NewPostHandler),
	("/blog/(\d+)", OldPostHandler),
	("/ascii", ASCIIHandler),
	("/", MainPage),
	],
	debug=True)