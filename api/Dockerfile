FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY OMDB_API_KEY .
COPY run.sh .

RUN source OMDB_API_KEY

EXPOSE 5000

CMD [ "/bin/bash", "run.sh" ]

#env FLASK_APP src/recommender-api.py

#CMD [ "flask", "run", "--host", "0.0.0.0" ]
