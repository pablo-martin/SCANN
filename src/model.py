from typing import Dict
from constants import model_path

from SmartEmbed.smartembed import SmartEmbed
from annoy import AnnoyIndex
from ranker import simple_ranker


SE = SmartEmbed()
ANN = AnnoyIndex(150, 'dot')
ANN.load(model_path)


def inference(smart_contract: str, K : int = 5, search_k : int = 20) -> Dict:
    #to-do: error checking, what if any step fails?
    
    # compute embedding
    embedding = SE.get_vector(smart_contract).reshape(-1)
    
    # ANN Retrieval
    neighbours = ANN.get_nns_by_vector(embedding, K * 4, search_k=search_k, include_distances=False)
    
    # Ranking
    ranked_NN = simple_ranker(embedding, neighbours, ANN, K=K)
    
    return ranked_NN