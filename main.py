from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
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

# Dono tarah ke routes handle kar lenge taaki 404 na aaye
@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        results = detector(temp_file_path)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        print("MODEL RESULTS:", results)
        top_result = results[0] if results else {"label": "real", "score": 0.0}
        label = top_result.get("label", "").lower()
        
        # Agar label 'real' ya 'bonafide' nahi hai, toh deepfake hai
        is_deepfake = "fake" in label or "spoof" in label or label != "real"
        
        return {
            "is_deepfake": is_deepfake,
            "message": f"Scan complete. Label: {label.upper()}"
        }
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
