import requests, json


url = "http://localhost/api/auth"

USERNAME = "me"
PASSWORD = ""

LANGUAGES = ['ENG','HAU','KAU']

BOT_STRINGS_SHEET = ""
NLU_SHEET = ""

payload = {
    "username": USERNAME,
    "password": PASSWORD
}

headers = {
    'content-type': "application/json",
}

response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

json_resp = response.json()

access_token = json_resp['access_token']


print('[info] generating files... ')

url = "http://localhost/custom/generate"

payload = {
    "bot_strings_sheet": BOT_STRINGS_SHEET,
	"nlu_sheet": NLU_SHEET,
	"lang": LANGUAGES
}

headers = {
    'content-type': "application/json",
    'authorization': "Bearer {access_token}".format(access_token=access_token)
}

response = requests.request("POST", url, data=json.dumps(payload), headers=headers)

print(response.text)

print('[info] files generated! ')

print('[info] training the model... ')


url = "http://localhost/custom/train"

headers = {
    'content-type': "application/json",
    'authorization': "Bearer {access_token}".format(access_token=access_token)
    }

response = requests.request("GET", url, headers=headers)

print(response.text)


