import ffmpeg
from pydantic import BaseModel
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
import os
import whisper
import hashlib
from pathlib import Path
import json
from better_profanity import profanity
from utils.mongo import insert, uploadFile
from uuid import uuid4


app = FastAPI()
model = whisper.load_model("tiny")  # Load model once during startup

"""
Represents an audio file and its associated file ID for transcription.

Parameters:
- `path`: The file path of the audio file.
- `file_id`: The unique identifier for the audio file.
"""
class AudioTranscriptModel(BaseModel):
    path: str
    file_id: str

def get_hash(audio_path):
    with open(audio_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

"""
Transcribes an audio file and stores the transcript in MongoDB.

Parameters:
- `data`: An `AudioTranscriptModel` instance containing the path to the audio file and the file ID.
- `background_tasks`: A `BackgroundTasks` instance to execute the audio transcription in the background.

Returns:
- A dictionary with the status of the transcript request and the transcript result.
"""
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
   
    return {"status": "file transcript requested!", "transcript": result}


"""
Uploads a file to the server and stores the file path in MongoDB.

Parameters:
- `file`: The uploaded file.

Returns:
- A dictionary with the status of the upload and the generated filename.
"""
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    # Generate a unique filename
    filename = file.filename.replace(" ", "")  # Remove whitespace characters
    unique_filename = f"{uuid4().hex}_{filename}"

    # Save the uploaded file
    upload_path = f"uploads/{unique_filename}"
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    uploadFile("/uploads/" + unique_filename)  # Insert the result into MongoDB
    return {"status": "file uploaded!", "filename": "/uploads/" + unique_filename}