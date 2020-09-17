from flask import Flask
from flask import jsonify
from .delphiClient import StorageClient
from .delphiClient import ApiHelper
import os

app = Flask(__name__)

REDIS_URL = os.environ.get("REDIS_URL")


# Setup storage client to read storage
store = StorageClient(None, REDIS_URL)
store.connect_to_storage()

# api helper setup
tools = ApiHelper(store)
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


@app.route("/apy")
def get_apy():
    try:
        apy = tools.get_apy()
        return jsonify(apy)
    except Exception as e:
        errormsg = f"Error while grabbing apy: {e}"
        print(errormsg)
        return jsonify({"Error": errormsg})


@app.route("/liquidity")
def get_liquidity():
    try:
        liquidity = tools.get_liquidity_total()
        return jsonify(liquidity)
    except Exception as e:
        errormsg = f"Error while grabbing liquidity: {e}"
        print(errormsg)
        return jsonify({"Error": errormsg})


@app.route("/rewards")
def get_rewards():
    try:
        rewards = tools.get_rewards()
        return jsonify(rewards)
    except Exception as e:
        errormsg = f"Error while grabbing stats: {e}"
        print(errormsg)
        return jsonify({"Error": errormsg})


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)