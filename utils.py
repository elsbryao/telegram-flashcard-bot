import os
import csv
import requests
import zipfile
from openai import OpenAI

output_dir = "output"
csv_filename = os.path.join(output_dir, "flashcards.csv")
zip_filename = "flashcards.zip"

def init_output():
    os.makedirs(output_dir, exist_ok=True)
    for f in os.listdir(output_dir):
        os.remove(os.path.join(output_dir, f))
    if os.path.exists(zip_filename):
        os.remove(zip_filename)

def text_to_speech(text, index, elevenlabs_api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": elevenlabs_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice_settings": {"stability": 0.4, "similarity_boost": 0.75}
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        path = os.path.join(output_dir, f"phrase_{index:02d}.mp3")
        with open(path, "wb") as f:
            f.write(response.content)

def save_and_zip(flashcards, elevenlabs_api_key, voice_id):
    with open(csv_filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Русский", "Английский"])
        for i, (ru, en) in enumerate(flashcards, 1):
            writer.writerow([ru, en])
            text_to_speech(en, i, elevenlabs_api_key, voice_id)
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        zipf.write(csv_filename, os.path.basename(csv_filename))
        for f in os.listdir(output_dir):
            if f.endswith(".mp3"):
                zipf.write(os.path.join(output_dir, f), f)

def extract_flashcards(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    return eval(response.choices[0].message.content)

def generate_flashcards_from_word(word, openai_key, eleven_key, voice_id):
    init_output()
    prompt = f"""
Подбери 5 хороших английских фраз с использованием слова "{word}" или его производных. 
Для каждой фразы сделай разговорный перевод всей фразы на русский.
Верни строго Python-список пар: [["русский", "английский"], ...]
"""
    flashcards = extract_flashcards(prompt, openai_key)
    save_and_zip(flashcards, eleven_key, voice_id)

def generate_flashcards_from_eng_phrases(phrases, openai_key, eleven_key, voice_id):
    init_output()
    joined = "\n".join(phrases)
    prompt = f"""
Вот список английских фраз:
{joined}

Для каждой фразы сделай хороший разговорный перевод на русский.

Верни строго Python-список пар в формате:
[
  ["русский перевод", "английская фраза"],
  ...
]

Никаких пояснений, только список!
"""
    flashcards = extract_flashcards(prompt, openai_key)
    save_and_zip(flashcards, eleven_key, voice_id)

def generate_flashcards_from_rus_phrases(phrases, openai_key, eleven_key, voice_id):
    init_output()
    joined = "\n".join(phrases)
    prompt = f"""Вот список русских фраз:\n{joined}\nСделай точный разговорный перевод на английский. Верни Python-список пар."""
    flashcards = extract_flashcards(prompt, openai_key)
    save_and_zip(flashcards, eleven_key, voice_id)
