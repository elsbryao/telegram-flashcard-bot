import csv
import os
import openai
import requests
import zipfile

output_zip = "flashcards.zip"

def generate_flashcards_from_word(word, openai_key, elevenlabs_key, voice_id):
    openai.api_key = openai_key
    prompt = f"Give 5 useful English example sentences using the word '{word}'."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    english_phrases = extract_phrases(response['choices'][0]['message']['content'])

    translation_prompt = "Translate the following English sentences to Russian:\n" + "\n".join(english_phrases)
    translation_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.7
    )
    translations = extract_phrases(translation_response['choices'][0]['message']['content'])

    return create_zip(translations, english_phrases, elevenlabs_key, voice_id)

def generate_flashcards_from_eng_phrases(phrases, openai_key, elevenlabs_key, voice_id):
    openai.api_key = openai_key
    translation_prompt = "Translate the following English sentences to Russian:\n" + "\n".join(phrases)
    translation_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.7
    )
    translations = extract_phrases(translation_response['choices'][0]['message']['content'])
    return create_zip(translations, phrases, elevenlabs_key, voice_id)

def generate_flashcards_from_rus_phrases(phrases, openai_key, elevenlabs_key, voice_id):
    openai.api_key = openai_key
    translation_prompt = "Translate the following Russian sentences to English:\n" + "\n".join(phrases)
    translation_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.7
    )
    english_phrases = extract_phrases(translation_response['choices'][0]['message']['content'])
    return create_zip(phrases, english_phrases, elevenlabs_key, voice_id)

def generate_flashcards_from_phrasal(phrasal_verb, openai_key, elevenlabs_key, voice_id):
    openai.api_key = openai_key
    prompt = f"Give 5 natural English example sentences using the phrasal verb '{phrasal_verb}'."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    english_phrases = extract_phrases(response['choices'][0]['message']['content'])

    translation_prompt = "Translate the following English sentences to Russian:\n" + "\n".join(english_phrases)
    translation_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": translation_prompt}],
        temperature=0.7
    )
    translations = extract_phrases(translation_response['choices'][0]['message']['content'])

    return create_zip(translations, english_phrases, elevenlabs_key, voice_id)

def create_zip(rus_phrases, eng_phrases, elevenlabs_key, voice_id):
    flashcards = list(zip(rus_phrases, eng_phrases))
    csv_path = "flashcards.csv"
    with open(csv_path, mode='w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Русская фраза", "Английская фраза"])
        writer.writerows(flashcards)

    if os.path.exists(output_zip):
        os.remove(output_zip)

    with zipfile.ZipFile(output_zip, 'w') as zipf:
        zipf.write(csv_path)

        for i, phrase in enumerate(eng_phrases, 1):
            audio_data = synthesize_with_elevenlabs(phrase, elevenlabs_key, voice_id)
            audio_path = f"phrase_{i}.mp3"
            with open(audio_path, 'wb') as f:
                f.write(audio_data)
            zipf.write(audio_path)
            os.remove(audio_path)

    os.remove(csv_path)
    return output_zip

def extract_phrases(text):
    lines = text.strip().split("\n")
    phrases = []
    for line in lines:
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
