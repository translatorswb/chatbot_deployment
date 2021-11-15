# FROM rasa/rasa:1.10.2
FROM python:3.7-stretch

ADD . /app

WORKDIR /app



RUN chown -R $USER:$USER /app 

RUN apt update -y
RUN apt upgrade -y



RUN pip install -r /app/requirements.txt


# RUN python -m spacy download en
RUN python -m nltk.downloader all

# ENTRYPOINT [ "python", "server.py", "run", "actions" ].
ENTRYPOINT [ "python", "server.py"]
# ENTRYPOINT [ "rasa", "run", "actions" ]
