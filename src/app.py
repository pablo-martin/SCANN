import sys
from collections import defaultdict
from dataclasses import dataclass
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from model import inference
import time
from datetime import datetime, timedelta

from db import SmartContractDB
from user_session import UserSession
from constants import smart_contract_db_path


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
CORS(app)  # , origins=['http://localhost:5174'])
SCDB = SmartContractDB(smart_contract_db_path)
US = UserSession()


@app.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    st = time.time()
    contract = request.json.get('contract')
    if not contract:
        return jsonify({'error': 'No contract provided'})
    
    US.flush_to_DB()
    ranked_NN, embedding, hashed_embedding = inference(contract)
    if isinstance(embedding, int): # this means that it was not able to compute embedding
        return jsonify({'error': "Could not process smart contract. Make sure it's valid."})
    
    # if embedding is not in DB, we want to know so we can add it
    user_contract_id = SCDB.find_contract_id(hashed_embedding)
    
    
    ranked_NN_by_name = {name.rsplit("_", 1)[-1]: name for name in ranked_NN.values()}
    
    US.record("hash_emb", hashed_embedding)
    for i in range(1, 6):
        US.record(f"contract_id{i}", list(ranked_NN.keys())[i - 1])
    US.record("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # record what smart_contract was searched, if in DB returns contract_id, if not -1
    # for re-training of index, we find all new smart contracts not in library and add them to our system
    US.record("user_contract_id", user_contract_id)

    elapsed = timedelta(seconds = time.time() - st)
    ms_elapsed = elapsed.seconds * 1000 + (elapsed.microseconds // 1000)
    US.record("latency", ms_elapsed)
    
    # to-do: display latency in the webpage
    app.logger.debug(f"inference latency {ms_elapsed}ms")
    return jsonify(ranked_NN_by_name)

@app.route('/click', methods=['POST'])
@cross_origin()
def click():
    contract_id = request.json.get('contract_id')
    if contract_id:
        US.USER_SESSION[f"clicked{contract_id}"] += 1
    else:
        return jsonify({'error': 'No contract_id provided'})
    return jsonify({'success': 'Contract clicked'})


@app.route('/like', methods=['POST'])
@cross_origin()
def like():
    contract_id = request.json.get('contract_id')
    value = int(request.json.get('value'))
    if contract_id:
        US.USER_SESSION[f"like{contract_id}"] += value
    else:
        return jsonify({'error': 'No contract_id provided'})
    return jsonify({'success': 'Contract liked'})




if __name__ == "__main__":
    app.run(debug=True)