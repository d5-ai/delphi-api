from flask import Flask
from flask import jsonify
import storageClient
import apiHelper
import os

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    # Setup storage client to read storage
    store = storageClient.StorageClient(None, REDIS_URL)
else:
    # local
    store = storageClient.StorageClient(None)
# api helper setup
tools = apiHelper.ApiHelper(store)
# Set up token prices
tools.update_token_prices()


@app.route("/")
def welcome():
    return jsonify({"result": "Welcome to delphi api powered by BigQuery and Nansen"})


@app.route("/stats")
def get_stats():
    try:
        stats = tools.get_stats()
        return jsonify(stats)
    except Exception as e:
        errormsg = f"Error while grabbing stats: {e}"
        print(errormsg)
        return jsonify({"Error": errormsg})