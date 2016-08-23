import webbrowser

class Video(object):
	"""This class provides a backbone for any class representing a video format.

	Attributes:
		title (str): The name of the Video.
		duration (int): The length in minutes of a given video.
	"""
	
	def __init__(self, title, duration):
		self.title = title
		self.duration = duration

class Movie(Video):
	"""This class provides a way to store movie related information.

	Attributes:
		storyline (str): The plotline of the movie.
		poster_image_url (str): Web address of the poster image for the Movie.
		trailer_youtube_url (str): Web address of the youtube trailer for the Movie.
	"""
	
	VALID_RATINGS = ["G","PG","PG-13","R"]
	
	def __init__(self, movie_title, movie_storyline, poster_image, trailer_youtube):
		Video.__init__(self, movie_title, 5)
		self.storyline = movie_storyline
		self.poster_image_url = poster_image
		self.trailer_youtube_url = trailer_youtube
		
	def show_trailer(self):
		webbrowser.open(self.trailer_youtube_url)