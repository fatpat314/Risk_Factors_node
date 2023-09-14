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
    # print(disease)
    KAN_url_risk_factors = f'{KAN_url}/GPT_risk_factors'
    data = {'disease': disease}
    response = requests.post(KAN_url_risk_factors, json=data)
    # print(response.json())
    risk_factors_list = response.json()
    # risk_factors_list = risk_factors_list.split('\n')
    # risk_factors_list = risk_factors_list[1:-1].split("', ")
    risk_factors_list = risk_factors_list[0].split('\n')
    print(type(risk_factors_list), risk_factors_list)

    CNM_url_risk_factors = f'{CNM_url}/risk_factors_disease'
    data = {'disease_name': disease, 'risk_factors_list': risk_factors_list}
    response = requests.post(CNM_url_risk_factors, json=data)
    print("HELLO")
    # return list of risk factors related to disease
    # if risk factor is shared by patient, add to another list

    return jsonify(risk_factors_list)

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
    print(response)
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
    print(response)
    return('hi')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8040, help="Port to run the server on")
    args = parser.parse_args()
    port = args.port
    app.run(host="0.0.0.0", port=port)