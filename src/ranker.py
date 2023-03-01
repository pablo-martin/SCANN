import numpy as np
from annoy import AnnoyIndex
from typing import List, Dict
from utils import read_yaml_file, array_to_hashlib

from db import SmartContractDB
from constants import smart_contract_db_path, user_session_db_path

SCDB = SmartContractDB(smart_contract_db_path)


def double_sigmoid(x): 
    return 2/(1 + np.exp(-x)) 

def cosine_similarity(a, b):
    return np.dot(a, b)/(np.linalg.norm(a)*np.linalg.norm(b))


def embeddings_cosine_similarity(input_embedding, res: List[int], ANN) -> Dict:
    return {
        _res: cosine_similarity(input_embedding, ANN.get_item_vector(_res)) 
        for _res in res
    }

def single_access(input_embedding_id):
    try:
        like_history = user_feedback[input_embedding_id]
        return like_history
    except KeyError:
        return dict()

def get_input_embedding_id(input_embedding):
    hashed_embedding = array_to_hashlib(input_embedding)
    try:
        return embhash_to_id[hashed_embedding]
    except KeyError:
        return -1
    
    
def rerank(cosine_similarities, likes_history, K=5):
    out = dict()
    for contract_id, cosine in cosine_similarities.items():
        try:
            reweight = cosine * double_sigmoid(likes_history[contract_id])
        except KeyError:
            reweight = cosine
        out[contract_id] = reweight
    return sorted(out.items(), key=lambda tup: tup[1], reverse=True)[:K]


def simple_ranker(input_embedding, res, ANN, K=5):
    cosine_similarities = embeddings_cosine_similarity(input_embedding, res, ANN)
    
    hashed_embedding = array_to_hashlib(input_embedding)
    likes_history = SCDB.find_contract_history(hashed_embedding)
    ranked_NN = rerank(cosine_similarities, likes_history, K=K)
    # return ranked predictions with contract names
    return {"prediction_text{}".format(ix): SCDB.find_contract_name(contract_id) 
            for ix, (contract_id, score) in enumerate(ranked_NN)}
