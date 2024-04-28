import random
import ffmpeg
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, Response
import os
import whisper
import hashlib
from pathlib import Path
import json
from better_profanity import profanity
from google.cloud import texttospeech
import json
import requests
import os
from utils.mongo import insert


app = FastAPI()
model = whisper.load_model("tiny")


class AudioConvertModel(BaseModel):
    path: str
    quality: str
    format: str


class AudioTrimModel(BaseModel):
    path: str
    start: int
    end: int
    format: str


class AudioTranscriptModel(BaseModel):
    path: str
    file_id: str


class AudioLanguageDetectModel(BaseModel):
    path: str


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.post("/transcript/")
async def transcript(data: AudioTranscriptModel, background_tasks: BackgroundTasks):
    hash = hashlib.md5(open(data.path, 'rb').read()).hexdigest()
    cache_path = "{}/cache/{}.bin".format(Path().absolute(), hash)

    def process_audio():
        result = model.transcribe(data.path)
        with open(cache_path, 'w') as f:
            f.write(json.dumps(result))
        insert(result, data.file_id)  # Insert the result into MongoDB

    if os.path.exists(cache_path):
        result = json.loads(open(cache_path, encoding="utf8", errors='ignore').read())
    else:
        background_tasks.add_task(process_audio)
        result = {}

    # flags = get_flags(result['text'])
    return {"status": "file transcript requested!", "transcript": result}

@app.post("/detect-language/")
async def detect_language(data: AudioLanguageDetectModel):
    file_url = data.path
    download_directory = "/tmp"
    try:
        file_name = os.path.basename(file_url)
        download_path = os.path.join(download_directory, file_name)

        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        with open(download_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(download_path)
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)

        # os.remove(download_path)
        return {
            "status": "success",
            "message": "file language detected",
            "language":  {max(probs, key=probs.get)}
        }
    except requests.HTTPError as e:
        response = {
            "status": "error",
            "message": "Failed to download the file",
            "error_details": str(e)
        }
        return response
    except whisper.WhisperException as e:
        response = {
            "status": "error",
            "message": "Failed to process audio",
            "error_details": str(e)
        }
        return response
        # return Response(content=response, status_code=500)
    except Exception as e:
        response = {
            "status": "error",
            "message": "Failed to detect language",
            "error_details": str(e)
        }
        return response

def get_flags(text):
    matchers = ['fuck','sex','ass']
    explicit = [s for s in text.split() if any(xs in s for xs in matchers)]
    return {
        "explicit": len(explicit) > 0,
        "censored_text" : profanity.censor(text)
    }


# @app.post('/tts')
# async def text_to_speech(data: dict):
#     input_text = data.get('text')

#     voice = texttospeech.VoiceSelectionParams(
#         language_code="en-US",
#         ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
#     )

#     audio_config = texttospeech.AudioConfig(
#         audio_encoding=texttospeech.AudioEncoding.MP3
#     )

#     synthesis_input = texttospeech.SynthesisInput(text=input_text)
#     response = texttospeech.TextToSpeechClient().synthesize_speech(
#         input=synthesis_input,
#         voice=voice,
#         audio_config=audio_config
#     )

#     output_file = "temp/{}.mp3".format(random.randint(111111, 999999))
#     with open(output_file, "wb") as out:
#         out.write(response.audio_content)
    
#     return {"status": "text converted to speech!", "path": output_file}