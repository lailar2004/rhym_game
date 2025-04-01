import pandas as pd
import numpy as np
import joblib
import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Load trained model
model = joblib.load("difficulty_model.pkl")

# Load rhyming words dataset and assign zero-based levels if missing
rhyming_words = pd.read_csv("rhyme_ds.csv")

if "Level" not in rhyming_words.columns:
    np.random.seed(42)
    rhyming_words["Level"] = np.random.randint(0, 10, rhyming_words.shape[0])  # 0 to 9 instead of 1 to 10
    rhyming_words.to_csv("rhyme_ds.csv", index=False)

# Define static folder for audio
AUDIO_FOLDER = "static/audio"

def get_audio_filename(word):
    filename = f"{word}.mp3"
    return f"/audio/{filename}" if os.path.exists(os.path.join(AUDIO_FOLDER, filename)) else None

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route("/get_word", methods=["GET"])
def get_word():
    level = request.args.get("level", default=0, type=int)  
    words_at_level = rhyming_words[rhyming_words["Level"] == level]

    if words_at_level.empty:
        return jsonify({"error": "No words available for this level"}), 400

    row = words_at_level.sample(1).iloc[0]

    random_options = rhyming_words[rhyming_words["Word2"] != row["Word2"]].sample(2)["Word2"].tolist()

    correct_answer = row["Word2"]

    options = [correct_answer] + random_options
    np.random.shuffle(options)

    word_audio = get_audio_filename(row["Word1"])
    correct_audio = get_audio_filename(correct_answer)

    print(f"Fetching words for Level {level}: Word = {row['Word1']}, Correct Answer = {correct_answer}, Options = {options}")

    return jsonify({
        "word": row["Word1"],
        "word_audio": word_audio,
        "options": options,
        "correct": correct_answer,
        "correct_audio": correct_audio,
        "level": level
    })

@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.json
    current_level = data.get("level")
    correct_answers = data.get("correct_answers")
    total_attempts = data.get("total_attempts")
    time_taken = data.get("time_taken")

    if None in [current_level, correct_answers, total_attempts, time_taken]:
        return jsonify({"error": "Missing data"}), 400

    features = pd.DataFrame([[current_level, time_taken, correct_answers, total_attempts]], 
                            columns=["Current_Level", "Time_Taken", "Correct_Answers", "Total_Attempts"])

    next_level = model.predict(features)[0]
    next_level = max(0, next_level)  

    print(f"Received Metrics -> Level: {current_level}, Time Taken: {time_taken}s, "
          f"Correct Answers: {correct_answers}, Total Attempts: {total_attempts}")
    print(f"Predicted Next Level: {int(next_level)}\n")

    return jsonify({"next_level": int(next_level)})

if __name__ == "__main__":
    app.run(debug=True)
