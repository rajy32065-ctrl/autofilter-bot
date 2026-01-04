from imdb import IMDb

ia = IMDb()

def get_movie(movie_name):
    try:
        movies = ia.search_movie(movie_name)
        if not movies:
            return None

        movie = movies[0]
        ia.update(movie)

        return {
            "title": movie.get("title"),
            "year": movie.get("year"),
            "rating": movie.get("rating"),
            "poster": movie.get("full-size cover url")
        }
    except:
        return None
