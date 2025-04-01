import pandas as pd
from gtts import gTTS
import os
import shutil  # To move files

# Load your Excel file
df = pd.read_csv("rhyme_ds.csv")

# Define the destination folder in your Flask project
flask_audio_folder = "/path/to/your-flask-project/static/audio"

# Ensure the Flask audio folder exists
os.makedirs(flask_audio_folder, exist_ok=True)

# Function to generate and move audio files
def generate_audio(word, filename):
    tts = gTTS(text=word, lang="en")
    temp_path = f"{filename}.mp3"
    tts.save(temp_path)
    
    # Move to Flask static folder
    final_path = os.path.join(flask_audio_folder, filename)
    shutil.move(temp_path, final_path)
    
    return f"/audio/{filename}.mp3"  # Return relative path

# Generate and move audio for each word
df["word1_audio"] = df["Word1"].apply(lambda w: generate_audio(w, w))
df["word2_audio"] = df["Word2"].apply(lambda w: generate_audio(w, w + "_rhyme"))

# Save the updated Excel file
df.to_excel("rhyming_words_with_audio.xlsx", index=False)

print("✅ Audio files generated and moved to Flask!")
