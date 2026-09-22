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
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Audio load karke 16kHz par resample karo
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

        # ASVspoof / MelodyMachine models use 'spoof' for fake and 'bonafide' for real
        if "spoof" in top_label or "fake" in top_label or "synthetic" in top_label or "ai" in top_label:
            if top_score > 0.25: # Strict check for fake
                is_deepfake = True
        elif "bonafide" in top_label or "real" in top_label:
            if top_score < 0.6: # Agar real hone ka confidence bhi kam hai toh doubt maano
                is_deepfake = True
            else:
                is_deepfake = False

        # Secondary sweep for safety
        for res in results:
            lbl = res.get("label", "").lower()
            scr = res.get("score", 0.0)
            if ("spoof" in lbl or "fake" in lbl) and scr > 0.35:
                is_deepfake = True

        message = f"Model Output: {top_label.upper()} ({top_score * 100:.1f}%)"
        
        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw": results
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
