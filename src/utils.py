import hashlib
import requests
from constants import raw_github_base
from typing import Dict

def read_contract(contract_path : str) -> str:
    with open(contract_path, "r") as f:
        return f.read()
    
def array_to_hashlib(arr):
    emb_str = "".join([str(_fl) for _fl in arr])
    return hashlib.sha256(bytes(emb_str, encoding='utf-8')).hexdigest()

def get_contract_text(path_contract):
    return requests.get(raw_github_base.format(path_contract)).text