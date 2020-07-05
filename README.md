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
