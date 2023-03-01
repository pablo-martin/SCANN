import os
from typing import Dict
import pandas as pd

from utils import array_to_hashlib

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


def embedding_hash_to_contract_id(df: pd.DataFrame) -> Dict:
    """
    unfortunately annoy library doesn't let one search if a single embedding is in the index
    and when it returns closest neighbours, it never considers original embedding
    we must have this extra structure to quickly look up whether an embedding has been seen or not
    in order to load the "likes" history
    """
    return (
        df
        .reset_index()
        [["hashlib", "contract_id"]]
        .set_index("hashlib")
        ["contract_id"]
        .to_dict()
    )

if __name__ == "__main__":
    df = load_batches(base_dir)
    df = preprocess(df)
    embedding_hash_to_contract_id = embedding_hash_to_contract_id(df)
    # save results