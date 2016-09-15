from security_features import *
from google.appengine.ext import db


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

class Post(db.Model):
	name = db.StringProperty(required=True)
	entry = db.TextProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

	@classmethod
	def by_created(cls):
		return Post.all().order('-created')

	@classmethod
	def by_name(cls, name):
		u = Post.all().filter("name =", name).get()
		return u

	@property
	def comments(self):
		return Comment.by_post_by_created(self.key().id())

	@property
	def likes(self):
		return Likes.count_by_post(pid=str(self.key().id()))

	def already_liked(self, username):
		return Likes.has_author(pid=str(self.key().id()), author=username)

class Comment(db.Model):
	author = db.StringProperty(required=True)
	content = db.TextProperty(required=True)
	post_id = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

	@classmethod
	def by_post_by_created(cls, pid):
		return Comment.all().filter("post_id =", str(pid)).order('-created')

class Likes(db.Model):
	author = db.StringProperty(required=True)
	post_id = db.StringProperty(required=True)

	@classmethod
	def count_by_post(cls, pid):
		return Likes.all().filter("post_id =", pid).count()

	@classmethod
	def has_author(cls, pid, author):
		return Likes.all().filter("post_id =", pid).filter("author =", author).count() > 0