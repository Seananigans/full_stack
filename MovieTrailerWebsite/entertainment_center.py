import media
import fresh_tomatoes

toy_story = media.Movie("Toy Story", 
	"A story of a boy and his toys that come to life",
	"http://ia.media-imdb.com/images/M/MV5BMDU2ZWJlMjktMTRhMy00ZTA5LWEzNDgtYmNmZTEwZTViZWJkXkEyXkFqcGdeQXVyNDQ2OTk4MzI@._V1_SY1000_SX670_AL_.jpg",# NOQA
	"https://www.youtube.com/watch?v=KYz2wyBy3kc")


avatar = media.Movie("Avatar","Another Michael Bay film",
	"https://upload.wikimedia.org/wikipedia/en/b/b0/Avatar-Teaser-Poster.jpg",
	"https://www.youtube.com/watch?v=uZNHIU3uHT4")


star_wars = media.Movie("Star Wars: A New Hope", "Luke Skywalker goes on "
	"a wacky adventure",
	"https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcSOw49ejhvxh8ORT85kuLPxY-qcqf-4_Hwdmwuao_jdMnsP0uvyRQ",# NOQA
	"https://www.youtube.com/watch?v=sGbxmsDFVnE")


movies = [toy_story, avatar, star_wars]

fresh_tomatoes.open_movies_page(movies)