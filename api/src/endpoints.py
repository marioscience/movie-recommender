import os
import service as service
from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
app.config['COURSE_HEADERS'] = 'Content-Type'

@app.route('/login')
@cross_origin()
def login_user():
    """ Simulate a user login in and create object for user """
    pass

@app.route('/api/getImdbKey/<title>')
@cross_origin()
def get_imdb_key(title):
    return service.get_movie_imdb_id(title)

@app.route('/api/getId/<title>')
@cross_origin()
def get_movie_id_by_title(title):
    return service.get_movie_id_by_title(title)

@app.route('/api/trending')
@cross_origin()
def trending():
    """ Route to get demographic based recommendation
        params: no params
        Return: top 10 movies by rating """
    return service.get_trending_movies()

@app.route('/api/similar/<movie_id>')
@cross_origin()
def similar_to_movie(movie_id):
    """ Route to get top ten similar movies given a movieId
        params: movieId
        Return: top ten movies similar to <movieId> """
    return service.get_top_10_similar(movie_id)

@app.route('/api/rate/<user_id>/<movie_id>')
@cross_origin()
def rate_movie_for_user(user_id, movie_id):
    """ Route to get predicted rating by user for a particular movie
        params: userId, movieId
        Return: rating of movie """
    return service.get_rating(user_id, movie_id)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
    # 0.0.0.0 makes docker container listen to all interfaces.
