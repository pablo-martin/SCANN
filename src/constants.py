import os

# paths
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "SCANN.ann")
smart_contract_db_path = os.path.join(base_dir, "tables/smart_contracts.db")
user_session_db_path = os.path.join(base_dir, "tables/user_session.db")
raw_github_base = "https://raw.githubusercontent.com/tintinweb/smart-contract-sanctuary-ethereum/master/{}"

# constants
K = 5