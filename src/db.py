import json
import sqlite3
from typing import Dict

from constants import user_session_db_path, smart_contract_db_path

user_session_col_names = [
    'user_id',
    'date',
    'latency',
    'user_contract_id',
    'clicked1',
    'clicked2',
    'clicked3',
    'clicked4',
    'clicked5',
    'like1',
    'like2',
    'like3',
    'like4',
    'like5',
    'contract_id1',
    'contract_id2',
    'contract_id3',
    'contract_id4',
    'contract_id5',
    'embedding',
    "hash_emb"
]
sql_insert = "INSERT INTO user_session VALUES (:" + ", :".join(user_session_col_names) + ")"

class UserSessionDB:
    def __init__(self, table_path=user_session_db_path):
        self.conn = sqlite3.connect(table_path, check_same_thread=False)
        self.c = self.conn.cursor()
        try:
            self.N = self.search_db("SELECT COUNT(*) FROM user_session")[0][0]
        except:
            self.create_table()

    def create_table(self):
        """
        latency: miliseconds
        """
        self.c.execute("""CREATE TABLE user_session (
            user_id integer,
            date string,
            latency int,
            user_contract_id integer,
            clicked1 integer,
            clicked2 integer,
            clicked3 integer,
            clicked4 integer,
            clicked5 integer,
            like1 integer,
            like2 integer,
            like3 integer,
            like4 integer,
            like5 integer,
            contract_id1 integer,
            contract_id2 integer,
            contract_id3 integer,
            contract_id4 integer,
            contract_id5 integer,
            embedding text,
            hash_emb text)""")
        
    def insert_db(self, user_session_dict: Dict):
        with self.conn:
            self.c.execute(sql_insert, user_session_dict)
            
    def search_db(self, sql_query: str):
        with self.conn:
            self.c.execute(sql_query)
            return self.c.fetchall()

    def close_connection(self):
        self.conn.close()
        

class SmartContractDB:
    """
    Smart Contract DB
    hash_emb : it's the hashed embedding for quick lookup - primary key for speed
    contract_id : unique immutable id for identifiying each specific contract in DB
    contract_name : extension to be able to download from smart-contract-sanctuary-ethereum. if smart contract is not there we won't be able to fetch in MVP. really i would want to add the entire code string in here, but the data was 54GB and it made things hard so i just fetch from the web. slow but for MVP i think it's acceptable tradeoff
    contract_history: jsonified dictionary of likes/dislikes to other contracts given by the user
    embedding: ideally i would like to store the embedding here as well. however, since the index has it, for now just to save on space i'm leaving it blank and just want to show intent.
    """
    def __init__(self, table_path=smart_contract_db_path):
        self.conn = sqlite3.connect(table_path, check_same_thread=False)
        self.c = self.conn.cursor()
        self.table_name = "smart_contracts"
        exists = self.search_db("SELECT name FROM sqlite_master WHERE type='table' AND name='{}';".format(self.table_name))
        if len(exists) == 0:
            self.create_table()

    
    def create_table(self):
        self.c.execute("""CREATE TABLE {} (
            hash_emb string PRIMARY KEY, 
            contract_id integer, 
            contract_name text,
            contract_history text,
            embedding text
            )""".format(self.table_name))
        
    def insert_db(self, hashemb_contract_id: Dict):
        with self.conn:
            self.c.execute("""INSERT INTO smart_contracts VALUES (
                :hash_emb, 
                :contract_id,
                :contract_name,
                :contract_history,
                :embedding
                )""", hashemb_contract_id)
            
    def find_contract_id(self, hash_emb) -> int:
        with self.conn:
            self.c.execute("SELECT contract_id FROM smart_contracts WHERE hash_emb=:hash_emb", {"hash_emb": hash_emb})
            result = self.c.fetchall()
            try:
                return result[0][0]
            except IndexError:
                return -1
            
        
    def find_contract_history(self, hash_emb) -> Dict:
        with self.conn:
            self.c.execute("SELECT contract_history FROM smart_contracts WHERE hash_emb=:hash_emb", {"hash_emb": hash_emb})
            result = self.c.fetchall()
            try:
                return {int(k): v for k, v in json.loads(result[0][0]).items()}
            except IndexError:
                empty_history = dict()
                return empty_history
            
    def find_contract_name(self, contract_id):
        with self.conn:
            self.c.execute("SELECT contract_name FROM smart_contracts WHERE contract_id=:contract_id", {"contract_id": contract_id})
            result = self.c.fetchall()
            try:
                return result[0][0]
            except IndexError:
                return ""

    def append_history(self, hash_emb: str, new_contract_info: Dict):
        """
        if embedding is in the DB, it updates the contract history
        to-do: if it is not present, it creates a new entry for it and updates contract history

        """

        embedding_id = self.find_contract_id(hash_emb)
        if embedding_id == -1: 
            return

        embedding_history = self.find_contract_history(hash_emb)
        embedding_history.update(new_contract_info)
        jsonify_history = json.dumps(embedding_history)
        with self.conn:
            self.c.execute("UPDATE smart_contracts SET contract_history=:contract_history WHERE hash_emb=:hash_emb",
                          {"hash_emb": hash_emb, "contract_history": jsonify_history})
        
    def search_db(self, sql_query: str):
        with self.conn:
            self.c.execute(sql_query)
            return self.c.fetchall()
    
    def close_connection(self):
        self.conn.close()

        
