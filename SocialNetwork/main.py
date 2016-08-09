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

"""HANDLERS FOR WEBPAGES"""
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
		# visits = 0
		# visit_cookie_str = self.request.cookies.get('visits')
		# if visit_cookie_str:
		# 	cookie_val = check_secure_val(visit_cookie_str)
		# 	if cookie_val:
		# 		visits = int(cookie_val)

		# visits += 1

		# new_cookie_val = make_secure_val(str(visits))

		# self.response.headers.add_header("Set-Cookie", "visits=%s" % new_cookie_val, expires="Thu, 01-Jan-1970 00:00:10 GMT")

		self.render("base.html", username="", email="")
		# if visits>=10:
		# 	self.write("You are the best ever! You've been here {} times".format(visits))
		# else:
		# 	self.write("Hello World! You've been here %s times." % visits)

class LogIn(db.Model):
	# username = db.StringProperty(required=True)
	# password = db.StringProperty(required=True)
	pass

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
			login = make_secure_val(username)
			if login:
				self.response.headers.add_header('Set-Cookie', 'username=%s; Path=/' % str(login))
				self.redirect("/welcome")
			else:
				self.redirect("/signup")

class WelcomeHandler(Handler):
	def get(self):
		username = self.request.cookies.get('username').split("|")[0]
		print username
		print make_secure_val(username.split("|")[0])
		print check_secure_val(username.split("|")[0])
		if check_secure_val(username):
			# self.render("welcome.html", username=username)
			self.redirect("/signup")
		else:
			self.render("welcome.html", username=username)

app = webapp2.WSGIApplication([
	("/", MainPage),
	("/signup", SignUpHandler),
	("/welcome", WelcomeHandler),
	], debug=True)