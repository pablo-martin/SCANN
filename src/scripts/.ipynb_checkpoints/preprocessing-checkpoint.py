import os
import sys
import time
from datetime import timedelta
import warnings
from tqdm import tqdm
from typing import Dict
import pandas as pd
import logging

from SmartEmbed.smartembed import SmartEmbed
warnings.filterwarnings("ignore")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("preprocessing.log")
    ]
)

smart_embed_dir = "/Users/pablo/Documents/Coding/company_challenges/OpenZeppelin/src/SmartEmbed"

# sys.path.append not working, need to cd instead
os.chdir(smart_embed_dir)
se = SmartEmbed()

def contract_path_gen(base_dir: str):
    for root,dirs,files in os.walk(base_dir, topdown=True):
        for _file in files:
            if _file.split(".")[-1] == "sol":
                yield os.path.join(root, _file)
    
def read_contract(contract_path : str) -> str:
    with open(contract_path, "r") as f:
        return f.read()
    
def get_embedding(contract_path: str) -> Dict:
    try:
        return {
            "contract_path": contract_path,
            "embedding": se.get_vector(read_contract(contract_path)).reshape(-1)}
    except: # be very broad here, we don't know what errors could happen 
        return dict()
    
def save_snapshot(df, file_path):
    df.to_parquet(file_path.format(len(df)))
    
def report_time(start_time, msg=""):
    elapsed = time.time() - start_time
    logging.info(f"{msg}time elapsed: {timedelta(seconds=elapsed)}")
    
    
def compute_embeddings(base_dir, output_path):
    logging.info("-"*80)
    n_contracts = sum([1 for _ in contract_path_gen(base_dir)])
    overall_start = time.time()
    batch_start = overall_start
    overall_failed_embeddings = 0
    batch_failed_embeddings = overall_failed_embeddings
    batch_size = 20000
    batch_id = 0
    
    batch_embeddings = list()
    for batch_n, contract_path in enumerate(contract_path_gen(base_dir)):
        embedding = get_embedding(contract_path)
        if len(embedding) > 0:
            batch_embeddings.append(embedding)
            
        else:
            batch_failed_embeddings += 1

        if len(batch_embeddings) % batch_size == 0:
            pd.DataFrame(batch_embeddings).to_parquet(output_path.format(batch_id))
            batch_id += 1
            report_time(batch_start, msg="[batch]: ")
            report_time(overall_start, msg="[overall]: ")
            overall_failed_embeddings += batch_failed_embeddings
            logging.info(f"# contracts that could not be embedded in batch: {batch_failed_embeddings}")
            logging.info(f"# contracts that could not be embedded in total: {overall_failed_embeddings}")
            # reset variables
            batch_failed_embeddings = 0
            batch_start = time.time()
            batch_embeddings = list()
            logging.info(f"completed {len(batch_embeddings)}/{n_contracts} embeddings.")
        
        
    return



if __name__ == "__main__":
    """
    python preprocessing.py --base_dir /Users/pablo/Documents/Coding/company_challenges/OpenZeppelin/smart-contract-sanctuary-ethereum/contracts --output_dir /Users/pablo/Documents/Coding/company_challenges/OpenZeppelin/src/embeddings  > /dev/null 2>&1
    """
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_dir", help="top-level directory to search for .sol files")
    parser.add_argument("--output_dir", help="directory to save parquet files")
    args = parser.parse_args()

    output_path = os.path.join(args.output_dir, "embeddings_batch{}.parquet")
    compute_embeddings(args.base_dir, output_path)
