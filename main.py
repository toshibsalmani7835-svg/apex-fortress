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

@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # File save karo
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Librosa se audio load karo aur 16kHz par resample karo (Model ke liye best hota hai)
        audio_array, sample_rate = librosa.load(temp_file_path, sr=16000)
        
        # Model ko direct numpy array pass karo librosa processing ke baad
        results = detector({"array": audio_array, "sampling_rate": sample_rate})
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        print("LIBROSA MODEL RESULTS:", results)
        
        is_deepfake = False
        highest_score = 0.0
        detected_label = "unknown"
        
        for res in results:
            label = res.get("label", "").lower()
            score = res.get("score", 0.0)
            if score > highest_score:
                highest_score = score
                detected_label = label
            
            # Check labels
            if "fake" in label or "spoof" in label or "ai" in label or "synthetic" in label:
                if score > 0.35:
                    is_deepfake = True

        # Agar model 'real' bol raha hai par confidence kam hai, toh doubt rakho
        if "real" in detected_label and highest_score < 0.65:
            is_deepfake = True

        message = f"Result: {detected_label.upper()} ({highest_score * 100:.1f}% confidence)"
        
        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw": results
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
