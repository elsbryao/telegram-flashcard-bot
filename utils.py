import csv
import os
import openai
import requests
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import shutil
import zipfile

output_zip = "flashcards.zip"

def generate_flashcards_from_phrasal(phrasal_verb, openai_key, elevenlabs_key, voice_id):
    openai.api_key = openai_key

    prompt = f"Give 5 natural English example sentences using the phrasal verb '{phrasal_verb}'."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    raw_output = response['choices'][0]['message']['content']
    english_phrases = extract_phrases(raw_output)

    # Перевод на русский
    translation_prompt = "Translate the following English sentences to Russian:\n" + "\n".join(english_phrases)
    translation_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.7
    )
    translations = extract_phrases(translation_response['choices'][0]['message']['content'])

    # Создаём CSV
    flashcards = list(zip(translations, english_phrases))
    csv_path = "flashcards.csv"
    with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Русская фраза", "Английская фраза"])
        writer.writerows(flashcards)

    # Озвучка и сбор в ZIP
    if os.path.exists(output_zip):
        os.remove(output_zip)

    with zipfile.ZipFile(output_zip, 'w') as zipf:
        zipf.write(csv_path)

        for i, phrase in enumerate(english_phrases, 1):
            audio_data = synthesize_with_elevenlabs(phrase, elevenlabs_key, voice_id)
            audio_path = f"phrase_{i}.mp3"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            zipf.write(audio_path)
            os.remove(audio_path)

    os.remove(csv_path)

def extract_phrases(text):
    lines = text.strip().split("\n")
    phrases = []
    for line in lines:
        # Удаление номеров: "1. text", "- text", "* text"
        cleaned = line.strip()
        if cleaned[:2].isdigit():
            cleaned = cleaned[2:].strip()
        cleaned = cleaned.lstrip("0123456789.-* ").strip()
        if cleaned:
            phrases.append(cleaned)
    return phrases

def synthesize_with_elevenlabs(text, api_key, voice_id):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.content
