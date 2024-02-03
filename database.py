from pymongo import MongoClient
import os

# Connect to MongoDB
mongo_client = MongoClient(os.getenv('mongodb'))
db = mongo_client['Cloner']
log = db['log']
sites_log = db['cloned']
