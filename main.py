from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import shutil
import os

app = FastAPI(title="Apex Fortress Backend")

# CORS Configuration taaki frontend seamlessly connect ho sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the Wav2Vec2 transformer model for deepfake audio detection
print("Loading Wav2Vec2 transformer model...")
detector = pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection")

@app.get("/")
def read_root():
    return {"status": "Apex Fortress Backend is online", "model": "Wav2Vec2"}

@app.post("/api/v1/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save uploaded audio file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Run transformer model inference
        results = detector(temp_file_path)
        
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        # Parse classification results
        top_result = results[0] if results else {"label": "unknown", "score": 0.0}
        label = top_result.get("label", "").lower()
        score = top_result.get("score", 0.0)
        
        # Determine if it's a deepfake
        is_deepfake = "fake" in label or "spoof" in label or "deepfake" in label
        message = f"Vocal frequency analyzed. Result: {label.upper()} (Confidence: {score:.2f})"
        
        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw_results": results
        }
        
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
