      from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import librosa
import numpy as np
import shutil
import os

app = FastAPI(title="Apex Fortress Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading deepfake audio detection model...")
detector = pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection")

@app.get("/")
def read_root():
    return {"status": "Online"}

# Sabhi possible route variations yahan daal diye hain taaki 404 kabhi na aaye
@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
@app.post("api/v1/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Librosa se audio load aur resample
        audio_array, sample_rate = librosa.load(temp_file_path, sr=16000)
        results = detector({"array": audio_array, "sampling_rate": sample_rate})
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        print("--- RAW MODEL RESULTS ---", results)
        
        is_deepfake = False
        top_label = "unknown"
        top_score = 0.0
        
        for res in results:
            label = res.get("label", "").lower()
            score = res.get("score", 0.0)
            if score > top_score:
                top_score = score
                top_label = label

        # Detection logic
        if "spoof" in top_label or "fake" in top_label or "synthetic" in top_label or "ai" in top_label:
            if top_score > 0.2:
                is_deepfake = True
        elif "bonafide" in top_label or "real" in top_label:
            if top_score < 0.6:
                is_deepfake = True

        message = f"Result: {top_label.upper()} ({top_score * 100:.1f}%)"
        
        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw": results
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
      
