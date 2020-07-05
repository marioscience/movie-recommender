import numpy as np
import pandas as pd
from surprise import Dataset
from ast import literal_eval
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movie_df = pd.read_csv('../input/tmdb_5000_movies.csv')
movie_credits_df = pd.read_csv('../input/tmdb_5000_credits.csv')

VECTORIZER = None
VECTORIZED_MATRIX = None
COSINE_SIMILARITY_MATRIX = None
MOVIE_ID_INDICES = None

def get_trending_movies():
    """ Calculate IMDB style weighted ratings and return the top ten rated"""
    movies = movie_df.copy()

    # Clean columns for result
    movies = movies.drop([
    'homepage', 'keywords', 'original_language', 'production_countries', 'original_title', 'revenue', 
    'spoken_languages', 'status', 'production_companies'
    ], axis='columns')
    movies['genres'] = movies['genres'].apply(literal_eval)
    
    avg_rating = movies['vote_average'].mean()
    min_vote_value = np.percentile(movies['vote_count'], 80)    
    movies = movies.loc[movies['vote_count'] >= min_vote_value]

    for index, row in movies.iterrows():
        movies.at[index, 'imdb_rating'] = calculate_weigthed_rating(row['vote_average'], min_vote_value, row['vote_count'], avg_rating)
    
    return movies.sort_values('imdb_rating', ascending=False).head(10).to_json(orient='records')

def get_top_10_similar(movie_id):
    movie_credits = movie_credits_df.drop(['title'], axis='columns')
    movies = movie_df.merge(movie_credits.rename({"movie_id": "id"}, axis='columns'), on='id')

    #print(movies.isnull().sum())
    for feature in ['homepage', 'overview', 'tagline']: 
        movies[feature] = movies[feature].fillna('')

    #if COSINE_SIMILARITY_MATRIX == None:
    VECTORIZER = TfidfVectorizer(stop_words='english')
    VECTORIZED_MATRIX = VECTORIZER.fit_transform(movies['overview'])
    COSINE_SIMILARITY_MATRIX = cosine_similarity(VECTORIZED_MATRIX)
    MOVIE_ID_INDICES = pd.Series(movies.index, index=movies['id']).drop_duplicates()

    # Give recommendation
    movie_similarity_vector = list(enumerate(COSINE_SIMILARITY_MATRIX[MOVIE_ID_INDICES[movie_id]]))
    movie_similarity_scores = sorted(movie_similarity_vector, key=lambda x: x[1], reverse=True)[1:11]
        
    return movies.iloc[[i[0] for i in movie_similarity_scores]].to_json(orient='records')

def get_rating(user_id, movie_id):
    return str(user_id) + " says " + str(movie_id)

def calculate_weigthed_rating(rating, minimum_votes, number_of_votes, avg_rating):
    """ 
    Calculate weigted rating as calculated in IMDB. 
    This rating accounts for the number of votes a movie has.
    """
    rhs = number_of_votes / (number_of_votes+minimum_votes)
    lhs = minimum_votes / (number_of_votes+minimum_votes)
    return (rhs * rating) + (lhs * avg_rating)

#def create_soup(dataframes=[dfs], labels=['lbls']):
    """ 
    Given a group of dataframes and a group of labels,
    check if the label is in each diagram (use df.colums.contains)
    then add it's values to the soup if they are strings. if they are objects
    try to iterate over values if they are string. return string with all
    string values. fields from dfs that can be used 'genres', keyowords, overview, important cast, important crew
    """
    #pass
    

if __name__ == "__main__":
    print(get_trending_movies()+ " | " +get_top_10_similar(42)+ " | " + get_rating(12, 42))
