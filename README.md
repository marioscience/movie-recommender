### Run locally
```
server:
cd /project/api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/recommender-api.py
```

### Run on Docker
```
cd /project/api
docker build --tag movie-recommend .
docker run -it -p 5000:5000 movie-recommend
```
### Create OMDB Api Key
Not used at the moment, but a requirement for the program to run: create a file with
the OMDB Api Key to use. (can be a simple dummy at the moment, not a real key)

create a file named OMDB_API_KEY under movie-recommender/api and add the following to it:
```
export OMDB_API_KEY="this_can_be_fake_for_now"
```
