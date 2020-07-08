### Run locally
```
server:
cd movie-recommender/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/recommender-api.py
```
Remember to run ``` source OMDB_API_KEY``` to set OMDB Api Key.

### Run on Docker
```
cd movie-recomender/api
docker build --tag movie-recommend .
docker run -it -p 5000:5000 movie-recommend
```

### docker-compose
```
cd movie-recommender/
docker-compose up
```
Remember to run ``` source OMDB_API_KEY``` to set OMDB Api Key.

### Currently implemented API endpoints
```
localhost:5000/api/trending
localhost:5000/api/similar/<movie_id>
localhost:5000/api/rate/<user_id>/<movie_id>
localhost:5000/api/getImdbKey/<title>
localhost:5000/api/getId/<title>
```

### Returned object
This is the object that is returned in each request. Either singly or as part of a list. Made uniform for simplicity. Can have appended attributes depending on request.
```
{
        "budget": 8000000,
        "genres": [
            {
                "id": 53,
                "name": "Thriller"
            },
            {
                "id": 80,
                "name": "Crime"
            }
        ],
        "id": 680,
        "overview": "A burger-loving hit man, his philosophical partner, a drug-addled gangster's moll and a washed-up boxer converge in this sprawling, comedic crime caper. Their adventures unfurl in three stories that ingeniously trip back and forth in time.",
        "popularity": 121.463076,
        "release_date": "1994-10-08",
        "runtime": 154.0,
        "tagline": "Just because you are a character doesn't mean you have character.",
        "title": "Pulp Fiction",
        "vote_average": 8.3,
        "vote_count": 8428,
        "imdb_rating": 8.0747382677,
        "imdb_id": "tt0110912"
}
```


### Create OMDB Api Key
Not used at the moment, but a requirement for the program to run: create a file with
the OMDB Api Key to use. (can be a simple dummy at the moment, not a real key)

create a file named OMDB_API_KEY under movie-recommender/api and add the following to it:
```
export OMDB_API_KEY="this_can_be_fake_for_now"
```
