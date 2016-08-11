import os
import random
import re
import string

import webapp2
import jinja2
import hmac


SECRET = "Bananas"

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)

from google.appengine.ext import db

"""VALIDATION FOR USERNAME, PASSWORDS, AND EMAIL"""
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(username):
    return USER_RE.match(username)

EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
	return not email or EMAIL_RE.match(email)

"""HASHING FOR COOKIES AND PASSWORDS."""
def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	val = h.split("|")[0]
	if h == make_secure_val(val):
		return val

def make_salt():
	return "".join(random.choice(string.letters) for _ in xrange(15))

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hmac.new(SECRET, name+pw+salt).hexdigest()
	return "%s|%s" %(h, salt)

def valid_pw(name, pw, h):
	salt = h.split("|")[1]
	return h == make_pw_hash(name, pw, salt)

"""DATABASE FOR USERNAME AND PASSWORDS"""
def users_key(group="default"):
	return db.Key.from_path('users', group)

class User(db.Model):
	name = db.StringProperty(required=True)
	pw_hash = db.StringProperty(required=True)
	email = db.StringProperty()

	@classmethod
	def by_id(cls, uid):
		return User.get_by_id(uid, parent=users_key())

	@classmethod
	def by_name(cls, name):
		u = User.all().filter("name =", name).get()
		return u

	@classmethod
	def register(cls, name, password, email=None):
		pw_hash = make_pw_hash(name, password)
		return User(parent=users_key(),
			name=name,
			pw_hash=pw_hash,
			email=email)

	@classmethod
	def login(cls, name, password):
		u = cls.by_name(name)
		if u and valid_pw(name, password, u.pw_hash):
			return u

"""HANDLERS FOR WEBPAGES"""
class Handler(webapp2.RequestHandler):
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


class MainPage(Handler):
	def get(self):
		self.render("base.html", username="", email="")

class SignUpHandler(Handler):
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
			u = User.register(name=username, password=password, email=email)
			u.put()
			self.login(u)
			self.redirect("/welcome")

class LoginHandler(Handler):
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

class LogoutHandler(Handler):
	def get(self):
		self.logout()
		self.redirect("/signup")

class WelcomeHandler(Handler):
	def get(self):
		username = self.read_secure_cookie("username")
		if self.user:
			self.render('welcome.html', username=self.user.name)
		else:
			self.redirect("/signup")


app = webapp2.WSGIApplication([
	("/", MainPage),
	("/signup", SignUpHandler),
	("/login", LoginHandler),
	("/welcome", WelcomeHandler),
	("/logout", LogoutHandler)
	], debug=True)