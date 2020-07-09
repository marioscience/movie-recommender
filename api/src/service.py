import os
import sys
import json
import os.path
import requests as req
import numpy as np
import pandas as pd
from surprise import Dataset
from ast import literal_eval
from surprise import Reader, Dataset, SVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

reader = Reader(line_format="user item rating", sep=",", skip_lines=1)
movie_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "input", "tmdb_5000_movies.csv"))
movie_credits_df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "input", "tmdb_5000_credits.csv"))
user_ratings_ds = Dataset.load_from_file(os.path.join(os.path.dirname(__file__), "..", "input", "ratings_small.csv"),
                                         reader=reader)

# global variables to be used only in this module
VECTORIZER = None
VECTORIZED_MATRIX = None
COSINE_SIMILARITY_MATRIX = np.array([])
MOVIE_ID_INDICES = None
SVD_MODEL = None


def get_list_of_movies(page):
    """
    Return a list of movies paginated.
    params: page
    returns: list of movie objects
    """
    pass


def get_movie_imdb_id(title, get_object=False):
    """

    """
    if "OMDB_API_KEY" in os.environ:
        OMDB_KEY = os.environ['OMDB_API_KEY']
    else:
        error_message = "ERROR: OMDB_API_KEY environment variable must be set, run 'source OMDB_API_KEY'" \
                        " after putting you key in it on project root directory"
        print(error_message, file=sys.stderr)
        return error_message, 500

    url = "http://www.omdbapi.com/?t=%s&apikey=%s" % (title, OMDB_KEY)
    res = json.loads(req.get(url).text)

    if get_object:
        return res

    imdb_id = res["imdbID"] if "imdbID" in res else "not_found"
    return imdb_id

def get_movie_poster_and_trailer(movie, get_trailer=False):
    """ Get movie and append poster image from tmdb API"""
    if "TMDB_API_KEY" in os.environ:
        TMDB_KEY = os.environ['TMDB_API_KEY']
    else:
        error_message = "Error TMDB API Key not set. Refer to documentation to add this"
        print(error_message, file=sys.stderr)
        return error_message, 500
    movie_id = movie['id']
    if not isinstance(movie_id, int):
        movie_id = movie['id'].iloc[0]

    # The URL for the poster has two parts, base_url+poster_size and actual URL. The first is found in config.
    tmdb_config_url = "https://api.themoviedb.org/3/configuration?api_key=%s" % TMDB_KEY
    #url = "https://api.themoviedb.org/3/movie/%s/images?api_key=%s" % (str(movie_id), TMDB_KEY)
    url = "https://api.themoviedb.org/3/movie/%s?api_key=%s&append_to_response=videos" % (str(movie_id), TMDB_KEY)

    config_res = json.loads(req.get(tmdb_config_url).text)["images"]
    res = json.loads(req.get(url).text)

    base_url = config_res["base_url"]
    poster_size = config_res["poster_sizes"][3]

    if res["poster_path"]:
        poster_url = res["poster_path"]
        movie['poster_url'] = base_url + poster_size + poster_url
    else:
        movie['poster_url'] = "https://www.publicdomainpictures.net/pictures/280000/velka/not-found-image-15383864787lu.jpg"

    if get_trailer:
        trailer_url_id = {}
        if res["videos"]["results"]:
            trailer_url_id = next(video for video in res["videos"]["results"] if video["type"] == "Trailer" and "teaser" not in video["name"].lower())
            if not trailer_url_id:
                trailer_url_id = res["videos"]["results"][0]

        if trailer_url_id and trailer_url_id["site"] == "YouTube":
            #movie["trailer_url"] = "https://www.youtube.com/watch?v=%s" % trailer_url_id["key"]
            movie["trailer_url"] = "https://www.youtube.com/embed/%s?autoplay=1" % trailer_url_id["key"]
        else:
            movie["trailer_url"] = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" #not found

    return movie


def get_movie_id_by_title(title):
    """
    Get the id for a movie title
    params: title
    returns: movie_id
    """
    return str(movie_df.loc[movie_df['title'] == title]['id'].iloc[0])


def get_trending_movies():
    """ 
    Calculate IMDB style weighted ratings and return the top ten rated
    params:
    returns: top ten movies by rating
    """
    # Clean columns for result
    movies = format_data_objects(movie_df.copy())

    avg_rating = movies['vote_average'].mean()
    min_vote_value = np.percentile(movies['vote_count'], 80)
    movies = movies.loc[movies['vote_count'] >= min_vote_value]

    for index, row in movies.iterrows():
        movies.at[index, 'imdb_rating'] = calculate_weigthed_rating(row['vote_average'], min_vote_value,
                                                                    row['vote_count'], avg_rating)

    top_ten_similar = movies.sort_values('imdb_rating', ascending=False).head(10)
    top_ten_similar = top_ten_similar.apply(get_movie_poster_and_trailer, axis=1)

    return append_imdb_id_to_df(top_ten_similar).to_json(orient='records')


def get_top_10_similar(movie_id, use_overview_for_similarity=False): ## Change back to False as default
    """
    Given a movie id, return the top 10 similar movies.
    params: movie id
    returns: json object of top 10 similar movies
    """
    global VECTORIZER
    global VECTORIZED_MATRIX
    global COSINE_SIMILARITY_MATRIX
    global MOVIE_ID_INDICES

    movies_with_credits = movie_credits_df.rename({"movie_id": "id"}, axis='columns').drop('title', axis='columns')
    # create optional variable to use soup or overview. create word soup here.

    movies = movie_df.copy()
    movies = movies.merge(movies_with_credits, on='id')

    # print(movies.isnull().sum())
    for feature in ['overview', 'tagline']:
        movies[feature] = movies[feature].fillna('')

    # Keep calculated objects in memory for performance
    if COSINE_SIMILARITY_MATRIX.size == 0:
        movies = movies.apply(create_movie_column_soup, axis=1)

        VECTORIZER = TfidfVectorizer(stop_words='english')
        if use_overview_for_similarity:
            VECTORIZED_MATRIX = VECTORIZER.fit_transform(movies['overview'])
        else:
            VECTORIZED_MATRIX = VECTORIZER.fit_transform(movies['column_soup'])
        COSINE_SIMILARITY_MATRIX = cosine_similarity(VECTORIZED_MATRIX)
        MOVIE_ID_INDICES = pd.Series(movies.index, index=movies['id']).drop_duplicates()

    movies = format_data_objects(movies)
    # Give recommendation
    movie_similarity_vector = list(enumerate(COSINE_SIMILARITY_MATRIX[MOVIE_ID_INDICES[int(movie_id)]]))
    movie_similarity_scores = sorted(movie_similarity_vector, key=lambda x: x[1], reverse=True)[1:11]
    top_ten_similar = movies.iloc[[i[0] for i in movie_similarity_scores]]
    top_ten_similar = append_imdb_id_to_df(top_ten_similar)
    top_ten_similar = top_ten_similar.apply(get_movie_poster_and_trailer, axis=1)

    return top_ten_similar.to_json(orient='records')


def get_rating(user_id, movie_id):
    """
    Docstring
    This method will compute a predicted rating given
    """
    global SVD_MODEL
    if SVD_MODEL is None:
        SVD_MODEL = SVD()
        trainset = user_ratings_ds.build_full_trainset()
        SVD_MODEL.fit(trainset)

    prediction = SVD_MODEL.predict(user_id, movie_id)

    movie = format_data_objects(movie_df.loc[movie_df['id'] == int(movie_id)])
    movie['predicted_rating'] = prediction.est
    movie['imdb_id'] = get_movie_imdb_id(movie['title'].iloc[0])
    movie = get_movie_poster_and_trailer(movie, get_trailer=True)
    return movie.to_json(orient='records')


def format_data_objects(dataframe):
    dataframe = dataframe.drop([
        'homepage', 'keywords', 'original_language', 'production_countries', 'original_title', 'revenue',
        'spoken_languages', 'status', 'production_companies', 'crew', 'cast', 'column_soup'
    ], axis='columns', errors='ignore')
    dataframe['genres'] = dataframe['genres'].apply(literal_eval)
    return dataframe


def append_imdb_id_to_df(dataframe):
    for index, row in dataframe.iterrows():
        dataframe.at[index, 'imdb_id'] = get_movie_imdb_id(row['title'])
    return dataframe


def calculate_weigthed_rating(rating, minimum_votes, number_of_votes, avg_rating):
    """ 
    Calculate weigted rating as calculated in IMDB. 
    This rating accounts for the number of votes a movie has.
    params: rating of item, min votes, num of votes for item, average rating of set containing item
    returns: IMDB rating (weighted by item vote count)
    """
    rhs = number_of_votes / (number_of_votes + minimum_votes)
    lhs = minimum_votes / (number_of_votes + minimum_votes)
    return (rhs * rating) + (lhs * avg_rating)


def create_movie_column_soup(movie):
    """ 
    Given a group of dataframes and a group of labels,
    check if the label is in each diagram (use df.colums.contains)
    then add it's values to the soup if they are strings. if they are objects
    try to iterate over values if they are string. return string with all
    string values. fields from dfs that can be used 'genres', keyowords, overview, important cast, important crew
    params: dataframe
    returns: dataframe with cleaned data
    """
    # serialize important cast names
    desired_crew_jobs = ['Original Music Composer', 'Director', 'Writer' ]
    genres = stringify_features(movie, 'genres').lower()
    keywords = stringify_features(movie, 'keywords').lower()
    overview = movie['overview'].lower()
    cast = ' '.join(['-'.join(i['name'].split(" ")) for i in sorted(literal_eval(movie['cast']), key=lambda x: x['order'])[0:10]]).lower()
    crew = ' '.join(['-'.join(i['name'].split(" ")) for i in literal_eval(movie['crew']) if i['job'] in desired_crew_jobs]).lower()
    # serialize important crew names departments:

    movie['column_soup'] = "%s %s %s %s %s" % (genres, keywords, overview, cast, crew)
    return movie

def stringify_features(items, feature, extract_feature='name'):
    return ' '.join(['-'.join(i[extract_feature].split(" ")) for i in literal_eval(items[feature])])


if __name__ == "__main__":
    print(get_trending_movies() + " | " + get_top_10_similar(42) + " | " + get_rating(12, 42))
