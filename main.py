from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import librosa
import torch
import torch.nn.functional as F
from transformers import Wav2Vec2FeatureExtractor, Wav2Vec2ForSequenceClassification
import os
import shutil

app = FastAPI(
    title="Apex Fortress Enterprise Beast Engine",
    version="3.0.0",
    description="Heavy-duty production transformer model for enterprise-grade audio deepfake detection."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Loading Heavy-Duty State-of-the-Art Deepfake Audio Classifier
MODEL_ID = "MelodyMachine/Deepfake-audio-detection"
print("🚀 Loading Beast-Mode Audio Transformer Model...")

try:
    feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(MODEL_ID)
    model = Wav2Vec2ForSequenceClassification.from_pretrained(MODEL_ID)
    model.eval()
    print("🔥 Beast Model Loaded Successfully & Ready for Combat!")
except Exception as e:
    print(f"❌ Error loading heavy model: {e}")
    model = None
    feature_extractor = None

@app.get("/")
def home():
    return {"status": "online", "engine": "Apex Fortress Heavy Transformer Core v3.0"}

@app.post("/api/v1/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # Securely save incoming audio stream
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Load audio strictly at 16kHz (Mandatory for Transformer audio models)
        y, sr = librosa.load(temp_file_path, duration=5.0, sr=16000)
        
        if len(y) < sr * 0.4:
            raise HTTPException(status_code=400, detail="Audio file is too short for deep neural inspection.")

        if model is None or feature_extractor is None:
            raise HTTPException(status_code=500, detail="Neural model not initialized on server.")

        # Process audio through Wav2Vec2 Feature Extractor
        inputs = feature_extractor(
            y, 
            sampling_rate=16000, 
            return_tensors="pt", 
            padding=True
        )

        # Run inference through the neural network
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probabilities = F.softmax(logits, dim=-1)

        # Extract confidence scores
        probs = probabilities[0].tolist()
        spoof_score = float(probs[-1]) * 100
        real_score = float(probs[0]) * 100

        # Decision threshold
        is_deepfake = spoof_score > 50.0
        confidence = round(spoof_score if is_deepfake else real_score, 2)
        
        # Cleanup temp file instantly
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        if is_deepfake:
            message = f"🚨 AI SPOOF DETECTED: Synthetic neural vocoder or cloned voice signature identified (Risk: {confidence}%)."
        else:
            message = f"✅ AUTHENTIC VOICE: Organic human vocal tract harmonics verified (Confidence: {confidence}%)."

        return {
            "status": "success",
            "is_deepfake": is_deepfake,
            "confidence": confidence,
            "message": message,
            "raw_probabilities": {
                "spoof_percentage": round(spoof_score, 2),
                "real_percentage": round(real_score, 2)
            }
        }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
