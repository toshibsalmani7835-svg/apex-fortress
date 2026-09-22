from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import shutil
import os

app = FastAPI(title="Apex Fortress - Neural ML Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Powerful Deepfake Audio Neural Model...")
# Official pre-trained deep learning audio classification model
detector = pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection")

@app.get("/")
def read_root():
    return {"status": "Online", "engine": "Apex Neural ML Core Active"}

@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # File ko safely temporary store karo
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Neural network pipeline inference
        results = detector(temp_file_path)
        
        # Cleanup temporary file immediately
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        print("RAW MODEL PREDICTION:", results)
        
        top_label = "unknown"
        top_score = 0.0
        
        for res in results:
            score = float(res.get("score", 0.0))
            if score > top_score:
                top_score = score
                top_label = res.get("label", "").lower()

        # Classification logic based on model labels (bonafide vs spoof)
        is_deepfake = False
        if any(keyword in top_label for keyword in ["spoof", "fake", "synthetic", "ai", "label_1"]):
            if top_score > 0.25:
                is_deepfake = True
        elif any(keyword in top_label for keyword in ["bonafide", "real", "human", "label_0"]):
            if top_score < 0.65:
                is_deepfake = True
            else:
                is_deepfake = False
        else:
            is_deepfake = top_score > 0.5

        verdict_text = "AI Deepfake / Cloned Voice" if is_deepfake else "Genuine Human Voice"
        message = f"Verdict: {verdict_text} ({top_score * 100:.1f}% Confidence)"

        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw": results
        }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
