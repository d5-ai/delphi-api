import storageClient
import apiHelper
from flask import Flask
from flask import jsonify


app = Flask(__name__)


# Setup storage client to read storage
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