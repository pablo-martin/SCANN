from datetime import datetime

from db import UserSessionDB, SmartContractDB
from constants import user_session_db_path, smart_contract_db_path


USDB = UserSessionDB(user_session_db_path)
SCDB = SmartContractDB(smart_contract_db_path)

class UserSession:
    """
    to-do this should inherit from the UserSessionDB 
    """
    def __init__(self):
        self.reset_session()
        
    def reset_session(self):
        self.reset = True
        self.USER_SESSION = {
            "user_id": 1,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "latency": 0,
            "user_contract_id": -1,
            "clicked1": 0,
            "clicked2": 0,
            "clicked3": 0,
            "clicked4": 0,
            "clicked5": 0,
            "like1": 0,
            "like2": 0,
            "like3": 0,
            "like4": 0,
            "like5": 0,
            "contract_id1": -1,
            "contract_id2": -1,
            "contract_id3": -1,
            "contract_id4": -1,
            "contract_id5": -1,
            "embedding": "",
            "hash_emb": ""
            
        }
    def record(self, key, value):
        self.reset = False
        self.USER_SESSION[key] = value
        
    def flush_SCDB_info(self):
        return {self.USER_SESSION[f"contract_id{ix}"] : self.USER_SESSION[f"like{ix}"] 
                for ix in range(1, 6)}
        
    def flush_to_DB(self):
        #save to DB here
        if self.reset == False:
            USDB.insert_db(self.USER_SESSION)
            # append likes/dislikes to contract DB
            new_contract_info = self.flush_SCDB_info()
            hashed_embedding = self.USER_SESSION.get("hash_emb")
            if hashed_embedding is not None:
                
                SCDB.append_history(hashed_embedding, new_contract_info)
        self.reset_session()
