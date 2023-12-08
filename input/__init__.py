import json

from flask import Flask, request
from ai.input import AiInput

from sessions.session import Session

app = Flask("input")


@app.route("/", methods=["POST"])
def ai_input():
    session = Session()
    session.input_queue.put(AiInput(request.json))
    return "Good job!", 200


@app.route("/rule", methods=["POST"])
def add_rule():
    session = Session()
    session.characters.get(request.json.get('character', 'Other Poop')).add_rule(request.json)
    return "Good job!", 200


@app.route("/rules", methods=["GET"])
def fetch_rules():
    session = Session()
    return json.dumps(session.user_rules.rules), 200
