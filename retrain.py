import requests, json



url = "http://localhost/api/auth"

USERNAME = "me"
PASSWORD = ""

LANGUAGES = ['ENG','HAU','KAU']

BOT_STRINGS_SHEET = "https://docs.google.com/spreadsheets/d/1dgWSkbLn-Sy5WNnZrNIxqUR0R-wW-KIFDskYrb_wpb0/edit#gid=79369888"
# BOT_STRINGS_SHEET = "https://docs.google.com/spreadsheets/d/1lzRVveXl3wOd5bX1Umdvcnb5pFI3ibHFpUK9ihMS2bw/edit#gid=79369888"
NLU_SHEET = "https://docs.google.com/spreadsheets/d/17jKT6O1GFQgQOWzFhDe8jEEbJBkUVhe7HK8eSNlbjlU/edit#gid=126915115"
# NLU_SHEET = "https://docs.google.com/spreadsheets/d/1vSna0LiofhTnvmUH4kcYqUV9Dg7QR5dZO4xXRuncA18/edit#gid=126915115"

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



print('[info] training the model... ')


url = "http://localhost/custom/train"

headers = {
    'content-type': "application/json",
    'authorization': "Bearer {access_token}".format(access_token=access_token)
    }

response = requests.request("GET", url, headers=headers)

print(response.text)


