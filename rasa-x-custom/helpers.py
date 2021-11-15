import requests, os
from settings import *
from datetime import datetime



RASA_X_HOST = os.environ.get('RASA_X_HOST')

def get_current_repo(request):
    url = f"{RASA_X_HOST}/api/projects/default/git_repositories"

    headers = {
        'authorization': f"{request.headers['authorization']}",
    }

    response = requests.request("GET", url, headers=headers)

    result = response.json()
    
    return result

    


def get_repo_status(request, repo_id):
    url = f"{RASA_X_HOST}/api/projects/default/git_repositories/{repo_id}/status"

    headers = {
        'authorization': f"{request.headers['authorization']}",
    }

    response = requests.request("GET", url, headers=headers)

    result = response.json()

    return result


def checkout_master(request, repo_id, branch):
    url = f"{RASA_X_HOST}/api/projects/default/git_repositories/{repo_id}/branches/{branch}"

    headers = {
        'authorization': f"{request.headers['authorization']}",
    }

    response = requests.request("PUT", url, headers=headers)

    return response
    


def commit_changes(request, current_repo_id, current_branch):
    dt = datetime.now()

    url = f"{RASA_X_HOST}/api/projects/default/git_repositories/{current_repo_id}/branches/{STAGING_BRANCH}_{str(dt.timestamp())}/commits"

    headers = {
        'authorization': f"{request.headers['authorization']}",
    }

    response = requests.request("POST", url, headers=headers)


    result = response.json()

    return result