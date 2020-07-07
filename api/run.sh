#!/bin/bash

export FLASK_APP=src/recommender-api.py
if [ "$1" != '-production' ]
then
	export FLASK_ENV=development
else
	export FLASK_ENV=production
fi

if [ -f OMDB_API_KEY ]
then
	source OMDB_API_KEY
else
	echo "No OMDB_API_KEY file found. Set 'export OMDB_API_KEY=Your_Key_Here' in movie-recommender/api/OMDB_API_KEY file. Get key: https://www.omdbapi.com/apikey.aspx"
fi

flask run --host 0.0.0.0
