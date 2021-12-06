
from sanic import Sanic
from sanic.response import json as json_response
from sanic import response
from sheet_to_rasa_v2 import generate_files
from helpers import *

import rasasheets


from subprocess import STDOUT, check_output, PIPE, Popen
import json

from settings import API_TOKEN

import requests

app = Sanic(name='rasa-x-custom')


@app.route("/rasalogs", methods=['GET'], strict_slashes=False)
def rasalogs_to_annotation(request):
    logs = logs_to_annotation()
    if logs == True:
        response = {"status": "success"}
        return json_response(response)

    if 'exception' in logs:
        response = {"status": "failed", "message": logs}
        return json_response(response)


@app.route("/train", methods=['GET', 'POST'], strict_slashes=False)
def train(request):
    data = request.json
    current_repo = get_current_repo(request)

    if 'exception' in current_repo:
        response = {"status": "failed", "message": current_repo}
        return json_response(response)

    current_repo_id = max([x['id'] for x in current_repo])

    current_repo_path = f'/app/git/{current_repo_id}'

    out = Popen(['/usr/local/bin/rasa', 'train', '--data', f'{current_repo_path}/data', '-c',
                f'{current_repo_path}/config.yml', '-d', f'{current_repo_path}/domain.yml', '--out', f'{current_repo_path}/models'])
    (output, err) = out.communicate()

    p_status = out.wait()

    models = os.listdir(f'{current_repo_path}/models/')

    latest_model = max(models)

    # curl -k -F "model=/app/custom_api/models/20200714-131649.tar.gz" "http://una-drc.translatorswithoutborders.org/api/projects/default/models?api_token=f7e254b94429e2b73654322eaa91272abd14d3ee"

    out = Popen(['curl', '-k', '-F', f'model=@{current_repo_path}/models/{latest_model}',
                'http://rasa-x:5002/api/projects/default/models?api_token={API_TOKEN}'], stdout=PIPE)
    (output, err) = out.communicate()

    output_dict = json.loads(output)

    p_status = out.wait()

    return json_response(output_dict)


@app.route("/generate", methods=['POST'], strict_slashes=False)
def generate(request):
    data = request.json

    current_repo = get_current_repo(request)

    if 'exception' in current_repo:
        response = {"status": "failed", "message": current_repo}
        return json_response(response)

    current_repo_id = max([x['id'] for x in current_repo])

    output_directory_path = f'/app/git/{current_repo_id}/'

    sm = rasasheets.SheetsModel(
        spreadsheet_links=[data['nlu_sheet'], data['bot_strings_sheet']],
        requested_languages=data['lang'])

    quiz = rasasheets.Quiz(sm)
    out_quiz_data_filepath = os.path.join(
        output_directory_path, 'quiz_data.json')
    quiz.write_quiz_to_file(out_quiz_data_filepath)
    sm.table_buttoned_qs = quiz.updated_buttoned_qs

    # Process more heavily, annotate, generate stories, make model closer to Rasa files
    rsm = rasasheets.RasaModel(sheets_model=sm,
                               annotate_regex_entities=True,
                               generate_stories=True,
                               include_annotated_examples=True)

    # Write files
    rasasheets.RasaWriter.write_rasa_files(rasa_model=rsm,
                                           output_directory_path=output_directory_path,
                                           output_data_dirname='data',
                                           domain_filename='domain.yml',
                                           nlu_filename='nlu.md',
                                           stories_filename='stories.md',
                                           session_expiration_time=60,
                                           carry_over_slots_to_new_session=True)

    response = {"status": "success"}

    return json_response(response)


@app.route("/webhooks/whatsapp/webhook", methods=['GET', 'POST'], strict_slashes=False)
def wapp_webhook(request):
    data = request.json

    # data = {'results':
    #     [{'from': 'bot_number',
    #         'to': 'user_number',
    #         'integrationType': 'WHATSAPP',
    #         # 'receivedAt': '2021-06-22T07:04:47.589+0000',
    #         'messageId': 'abc',
    #         # 'pairedMessageId': None,
    #         # 'callbackData': None,
    #         'message': {'text': 'symptoms', 'type': 'TEXT'},
    #         # 'contact': {'name': 'user_name'},
    #         # 'price': {'pricePerMessage': 0.0, 'currency': 'NGN'}
    #         }],
    #         # 'messageCount': 1, 'pendingMessageCount': 195

    #         }

    print(data)

    url = "http://rasa-production:5005/webhooks/whatsapp/webhook"

    payload = json.dumps(data)
    headers = {
        'content-type': "application/json",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    responses = response.json()

    url = INFOBIP_URL
    headers = {
        'authorization': f"App {INFOBIP_AUTH_TOKEN}",
        'accept': "application/json",
        'content-type': "application/json",
    }

    for resp in responses:
        print(resp)

        # To fix delay in responses you can add a sleep function here
        # for a few milliseconds

        payload = {
            "destinations": [
                {
                    "messageId": data['results'][0]['messageId'],
                    "to": {
                        "phoneNumber": data['results'][0]['from']
                    }
                }
            ],
            "scenarioKey": INFOBIP_SCENARIO_KEY,
            "whatsApp": {
                # to modify text template to button or something
                "text": resp['text']
            }

        }

        response = requests.request(
            "POST", url, data=json.dumps(payload), headers=headers)

        print(response.text)

    return json_response(data)
