# FROM rasa/rasa-x:0.29.1
# FROM rasa/rasa:1.10.0-full
FROM python:3.7-stretch
#FROM python:3.8

ADD . /app/custom_api/
WORKDIR /app/custom_api/

RUN apt update -y
RUN apt upgrade -y

RUN chown -R $USER:$USER /app 
# RUN chown -R $USER:$USER /opt/venv/bin/pip

RUN pip install  --upgrade pip 

#RUN pip install rasa==2.2.5

RUN pip install rasa==2.5.0

RUN pip install -r requirements.txt 


CMD ["python", "/app/custom_api/wsgi.py"]
