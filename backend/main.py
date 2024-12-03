from pymongo import MongoClient
from os import getenv
from flask import Flask, request
from dotenv import load_dotenv

from accounts import begin_signup, authorize_token

load_dotenv()

database = MongoClient(getenv("MONGO_DB_URI"))["BetterMUN"]
app = Flask(__name__)


# Accounts

@app.route("/api/sign_up")
def signup():
    information = request.json()


if __name__ == "__main__":
    app.run(port=8088, debug=False)