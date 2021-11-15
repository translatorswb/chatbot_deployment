import sys, os
from settings import *
from main_service import app





"""
Custom API

/generate
generate files from strings-to-rasa.py and sync them with github

payload: nothing, as we can have the sheet configured in the backend and we will 
be using that only

response:
{
    "status":"success"
}



/train
Trains the model with the files generated

payload: nothing
response:
{
    "model":"20200528-164424.tar.gz",
    "status":"success"
}

/generate-logs
Generate conversation logs which we run through ~/conversation_logs/run.sh

payload: nothing
response:
{
    "sheet":"sheet-url",
    "status":"success"
}

"""


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)