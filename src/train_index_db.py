import os
import sys
from typing import Dict
import pandas as pd
from tqdm import tqdm
from annoy import AnnoyIndex

from db import SmartContractDB
from utils import array_to_hashlib
from constants import base_dir, smart_contract_db_path, model_path


sanctuary_base = "/Users/pablo/Documents/Coding/company_challenges/OpenZeppelin/smart-contract-sanctuary-ethereum/"
base_dir = "src/embeddings/"

def load_batches(base_dir : str) -> pd.DataFrame:
    batches = list()
    for _file in os.listdir(base_dir):
        if os.path.basename(_file).split(".")[-1] == "parquet":
            batches.append(pd.read_parquet(os.path.join(base_dir, _file)))

    return (
        pd.concat(batches)
        .reset_index(drop=True)
    )

def get_contract_name(full_path_contract):
    return full_path_contract.replace(sanctuary_base, "")

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    
    df["hashlib"] = df["embedding"].apply(array_to_hashlib)
    df["contract_path"] = df["contract_path"].apply(get_contract_name)
    return (
        df[["hashlib", "contract_path", "embedding"]]
        .drop_duplicates(subset=["hashlib"])
        .rename_axis("contract_id")
    )


def train_index_build_DB(df, n_trees=10):
    # initialize DB + index
    SCDB = SmartContractDB(smart_contract_db_path)
    ANN = AnnoyIndex(150, 'dot')
    ANN.set_seed(42)
    
    for ix, row in tqdm(df.iterrows()):
        payload = {
            'hash_emb': row["hashlib"],
             'contract_id': ix,
             'contract_history': '{}',
             'contract_name': row["contract_path"],
             'embedding': None
        }
        SCDB.insert_db(payload)
        ANN.add_item(ix, row["embedding"])

    ANN.build(10, n_jobs=-1)
    ANN.save(model_path)

def train_from_scratch(base_dir):
    df = load_batches(base_dir)
    df  = preprocess(df)
    train_index_build_DB(df)


def retrain(current_ANN):
    """
    this is a quick mockup of re-training process:
    given more time i might use airflow/prefect to make this a batch process either
    nightly, or given a certain threshold of new entries. implementation would be:
    
    1) embeddings are stored in index and match contract_ids in smart contract DB
    2) get new embeddings from user session DB
    3) iterate through both structures to recover data already trained. it is critical
    that the existing contract_ids remain the same since they must match the smart contract
    history in order to retain those valuable likes/dislikes
    4) append new data at the bottom, generating new contract_ids
    5) run train_index_build_DB, which will save files to default locations and 
    everything should work as before, but with the new previously unseen contract data
    """
    pass



if __name__ == "__main__":
    # to-do mock up argparse command line to specify training from scratch or retraining
    # for training from scratch i precomputed all embeddings into this folder
    embedding_batch_dir = "embeddings/"
    train_from_scratch(embedding_batch_dir)