from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoProcessor, AutoModelForAudioClassification
import torch
import librosa
import shutil
import os

app = FastAPI(title="Apex Fortress - Pure Neural ML Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading Pure Deepfake Neural Model and Processor...")
MODEL_NAME = "MelodyMachine/Deepfake-audio-detection"
processor = AutoProcessor.from_pretrained(MODEL_NAME)
model = AutoModelForAudioClassification.from_pretrained(MODEL_NAME)
model.eval()  # Set model to evaluation mode

@app.get("/")
def read_root():
    return {"status": "Online", "engine": "Pure Neural Network Inference"}

@app.post("/api/v1/scan-voice")
@app.post("/scan-voice")
async def scan_voice(file: UploadFile = File(...)):
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Load audio natively via librosa at standard 16kHz
        speech_array, sampling_rate = librosa.load(temp_file_path, sr=16000, mono=True)
        
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        # 2. Process audio through the model's official processor
        inputs = processor(
            speech_array, 
            sampling_rate=16000, 
            return_tensors="pt", 
            padding=True
        )

        # 3. Direct Neural Network Forward Pass (Pure AI Inference)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            # Convert logits to probabilities using softmax
            probabilities = torch.softmax(logits, dim=-1)[0]
            
        # 4. Get the exact predicted class directly from the model weights
        predicted_class_id = torch.argmax(probabilities).item()
        confidence_score = probabilities[predicted_class_id].item()
        
        # Fetch native label straight from model configuration config
        model_label = model.config.id2label.get(predicted_class_id, str(predicted_class_id)).lower()

        print(f"--- PURE ML INFERENCE --- Label: {model_label} | Score: {confidence_score:.4f} | Class ID: {predicted_class_id}")

        # Pure neural decision based strictly on model classification
        is_deepfake = False
        if "spoof" in model_label or "fake" in model_label or predicted_class_id == 1:
            is_deepfake = True
        else:
            is_deepfake = False

        verdict_text = "AI Deepfake / Cloned Voice" if is_deepfake else "Genuine Human Voice"
        message = f"AI Model Verdict: {verdict_text} ({confidence_score * 100:.1f}% Confidence)"

        return {
            "is_deepfake": is_deepfake,
            "message": message,
            "model_label": model_label,
            "confidence": float(confidence_score)
        }

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
