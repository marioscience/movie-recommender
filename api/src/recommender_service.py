import os
import sys
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
    res = literal_eval(req.get(url).text)

    if get_object:
        return res

    imdb_id = res["imdbID"] if "imdbID" in res else "not_found"
    return imdb_id


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

    return append_imdb_id_to_df(top_ten_similar).to_json(orient='records')


def get_top_10_similar(movie_id, use_overview_for_similarity=True): #change use_overview to False...
    """
    Given a movie id, return the top 10 similar movies.
    params: movie id
    returns: json object of top 10 similar movies
    """
    global VECTORIZER
    global VECTORIZED_MATRIX
    global COSINE_SIMILARITY_MATRIX
    global MOVIE_ID_INDICES

    movie_with_credits = movie_credits_df.rename({"movie_id": "id"})
    # create optional variable to use soup or overview. create word soup here.

    movies = movie_df.copy()
    movies['soup'] = ''

    # print(movies.isnull().sum())
    for feature in ['overview', 'tagline']:
        movies[feature] = movies[feature].fillna('')

    # Keep calculated objects in memory for performance
    if COSINE_SIMILARITY_MATRIX.size == 0:
        VECTORIZER = TfidfVectorizer(stop_words='english')
        if use_overview_for_similarity:
            VECTORIZED_MATRIX = VECTORIZER.fit_transform(movies['overview'])
        else:
            VECTORIZED_MATRIX = VECTORIZER.fit_transform(movies['soup'])
        COSINE_SIMILARITY_MATRIX = cosine_similarity(VECTORIZED_MATRIX)
        MOVIE_ID_INDICES = pd.Series(movies.index, index=movies['id']).drop_duplicates()

    movies = format_data_objects(movies)
    # Give recommendation
    movie_similarity_vector = list(enumerate(COSINE_SIMILARITY_MATRIX[MOVIE_ID_INDICES[int(movie_id)]]))
    movie_similarity_scores = sorted(movie_similarity_vector, key=lambda x: x[1], reverse=True)[1:11]
    top_ten_similar = movies.iloc[[i[0] for i in movie_similarity_scores]]

    return append_imdb_id_to_df(top_ten_similar).to_json(orient='records')


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

    return movie.to_json(orient='records')


def format_data_objects(dataframe):
    dataframe = dataframe.drop([
        'homepage', 'keywords', 'original_language', 'production_countries', 'original_title', 'revenue',
        'spoken_languages', 'status', 'production_companies', 'soup'
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


def create_movie_column_soup(movie, features):
    """ 
    Given a group of dataframes and a group of labels,
    check if the label is in each diagram (use df.colums.contains)
    then add it's values to the soup if they are strings. if they are objects
    try to iterate over values if they are string. return string with all
    string values. fields from dfs that can be used 'genres', keyowords, overview, important cast, important crew
    params: dataframe
    returns: dataframe with cleaned data
    """
    soup = ""
    for feature in features:
        next = movie[feature]
        if isinstance(next, str):
            next = list([next])
        soup += ' '.join(next)


if __name__ == "__main__":
    print(get_trending_movies() + " | " + get_top_10_similar(42) + " | " + get_rating(12, 42))
