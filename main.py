import config
from dotenv import load_dotenv
from flask import Flask, jsonify, request, session, g
from flask_jwt_extended import JWTManager, jwt_required, \
                               create_access_token, get_jwt_identity
import requests, names, random, threading, uuid, json
import argparse
import ast

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = config.JWT_SECRET_KEY # change this to a random string in production
CNM_url = "http://localhost:6000"
KAN_url = "http://localhost:8050"
jwt = JWTManager(app)
load_dotenv()

@app.route('/', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        data = "Risk Factor Node!"
        return jsonify({'data': data})

@app.route('/risk_factors', methods = ['GET', 'POST'])
@jwt_required()
def disease_risk_factors():
    disease = request.json.get('disease_name')
    patient_id = request.json.get('patientID')
    KAN_url_risk_factors = f'{KAN_url}/GPT_risk_factors'
    data = {'disease': disease}
    response = requests.post(KAN_url_risk_factors, json=data)
    # print(response.json())
    risk_factors_list = response.json()
    # risk_factors_list = risk_factors_list.split('\n')
    # risk_factors_list = risk_factors_list[1:-1].split("', ")
    original_list = risk_factors_list[0].split('\n')
    # print(type(risk_factors_list), risk_factors_list)
    risk_factors_list = [string.split('. ', 1)[1] if '. ' in string else string for string in original_list]

    CNM_url_risk_factors = f'{CNM_url}/risk_factors_disease'
    data = {'disease_name': disease, 'risk_factors_list': risk_factors_list, 'patient_id': patient_id}
    response = requests.post(CNM_url_risk_factors, json=data)
    print("HELLO")
    risk_factors_name_lists = response.json()
    # return list of risk factors related to disease
    # if risk factor is shared by patient, add to another list
    disease_id = risk_factors_name_lists[2]
    risk_id_list = risk_factors_name_lists[3]
    # event
    event_url = get_event_server(CNM_url)
    event_url = event_url['url']
    event_url = f'{event_url}/event-risk-disease'
    data = {'risk_factors_id': risk_id_list, 'disease_id': disease_id}
    event_response = requests.post(event_url, json=data)



    return jsonify(risk_factors_name_lists)

@app.route('/risk_factors_process', methods=['GET', 'POST'])
@jwt_required()
def risk_factors_patient_relationship():
    data = request.get_json()
    risk_factors = data['selectedItems']
    patient_id = data['patientID']
    print("RISK: ", risk_factors)
    CNM_url_risk_factors = f'{CNM_url}/risk_factors'
    data = {'risk_factors': risk_factors, 'patient_id': patient_id}
    response = requests.post(CNM_url_risk_factors, json=data)
    risk_factors_id_list = response.json()
    # event
    event_url = get_event_server(CNM_url)
    event_url = event_url['url']
    event_url = f'{event_url}/event-risk'
    data = {'patient_id': patient_id, 'risk_factors_id': risk_factors_id_list}
    event_response = requests.post(event_url, json=data)
    return('hi')

@app.route('/risk_factors_input', methods=['GET', 'POST'])
@jwt_required()
def risk_factor_input():
    data = request.get_json()
    risk_factors = data['riskFactorsData']
    patient_id = data['patientID']
    print(risk_factors, patient_id)
    
    CNM_url_risk_factors = f'{CNM_url}/risk_factors_input'
    data = {'risk_factors': risk_factors, 'patient_id': patient_id}
    response = requests.post(CNM_url_risk_factors, json=data)
    print("RF LIST:", response.json())
    risk_factors_id_list = response.json()

    # event
    event_url = get_event_server(CNM_url)
    event_url = event_url['url']
    event_url = f'{event_url}/event-risk'
    data = {'patient_id': patient_id, 'risk_factors_id': risk_factors_id_list}
    event_response = requests.post(event_url, json=data)
    return('hi')



def get_event_server(cloud_url):
    event_url = f'{cloud_url}/event_server'
    response = requests.get(event_url)
    return response.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8040, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)