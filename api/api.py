import joblib
import pandas as pd
from flask import Flask, request, jsonify
import json
import os

from mistralai import Mistral

# To run the API, run `flask --app api --debug run`
# Go to http://127.0.0.1:5000/api/gender to see the result

app = Flask(__name__)

GENDERS = {1: "M", 2: "F"}

def vectorize(name):
    alphabet = "abcdefghijklmnopqrstuvwxyz"

    return pd.Series([int(letter in name.lower()) for letter in alphabet])


@app.route("/api/gender")
def gender():
    name = request.args.get('name', None)

    if name is None:
        return "Please provide a name", 400

    regr = joblib.load("model.prenoms.bin")
    vector = vectorize(name)
    prediction = regr.predict([vector])[0]
    gender = GENDERS[prediction]

    return jsonify({
        "name": name,
        "gender": gender,
    })

@app.route("/api/gender/llm/")
def gender_llm():
    name = request.args.get('name', None)

    if name is None:
        return "Please provide a name", 400

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

    client = Mistral(api_key=MISTRAL_API_KEY)

    chat_response = client.chat.complete(
        model="mistral-large-latest",
        messages=[
            {
                "role": "system",
                "content": """
                You are a agent that have to guess the gender of a given name.
                If a name is both, just return B.
                
                Examples:
                For "Christophe" returns {"gender": "M"}.
                For "Marie" returns {"gender": "F"}.
                For "Camille" returns {"gender": "B"}.
                
                Just return a valid JSON response with no ```.
                """,
            },
            {
                "role": "user",
                "content": name,
            },
        ]
    )

    try:
        return jsonify(json.loads(chat_response.choices[0].message.content))
    except Exception as error:
        return jsonify({"error": "An error occured", "message": str(error)}), 200

