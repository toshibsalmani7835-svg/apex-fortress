from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
import shutil
import os

app = FastAPI(title="Apex Fortress - AI Neural Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading official Deepfake Audio ML Model from Hugging Face...")
# Asli pre-trained deep learning model load ho raha hai
detector = pipeline("audio-classification", model="MelodyMachine/Deepfake-audio-detection")

@app.get("/")
def read_root():
    return {"status": "Online", "engine": "AI Neural Model Active"}

@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # File ko temporarily save karo
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Direct Machine Learning Model Inference
        # Model apne aap audio features analyze karke score dega
        raw_results = detector(temp_file_path)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        print("ML MODEL RAW OUTPUT:", raw_results)
        
        # Parse model results
        top_label = "unknown"
        top_score = 0.0
        
        for res in raw_results:
            score = float(res.get("score", 0.0))
            if score > top_score:
                top_score = score
                top_label = res.get("label", "").lower()

        # Decision based strictly on the AI model's output labels (bonafide vs spoof/fake)
        is_deepfake = False
        if any(keyword in top_label for keyword in ["spoof", "fake", "synthetic", "ai", "label_1"]):
            if top_score > 0.30:
                is_deepfake = True
        elif any(keyword in top_label for keyword in ["bonafide", "real", "human", "label_0"]):
            if top_score < 0.60: # Agar real hone par model 100% sure nahi hai
                is_deepfake = True
            else:
                is_deepfake = False
        else:
            is_deepfake = top_score > 0.5

        verdict_text = "AI Deepfake / Cloned Voice" if is_deepfake else "Genuine Human Voice"
        message = f"AI Verdict: {verdict_text} ({top_score * 100:.1f}% Model Confidence)"

        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "raw": raw_results
        }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print("MODEL ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
