import os
from pymongo import MongoClient
from urllib import parse
from dotenv import load_dotenv
load_dotenv()  # loading enviromental variable from .env files

# Getting Credentials from Enviromental Variables in .env file
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

username = parse.quote_plus(DB_USERNAME)
password = parse.quote_plus(DB_PASSWORD)

## Connecting to Mongo Database Setup
cluster = MongoClient("mongodb://{}:{}@cluster1-shard-00-00.xwjgf.mongodb.net:27017,cluster1-shard-00-01.xwjgf.mongodb.net:27017,cluster1-shard-00-02.xwjgf.mongodb.net:27017/?ssl=true&replicaSet=atlas-1287r0-shard-0&authSource=admin&retryWrites=true&w=majority".format(username, password))

db = cluster.signalNFX