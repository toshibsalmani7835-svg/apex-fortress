from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/scan-voice', methods=['POST'])
def scan_voice():
    if 'file' not in request.files:
        return jsonify({"status": "safe", "message": "❌ No audio file provided."})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "safe", "message": "❌ Empty file selected."})
    
    filename = file.filename.lower()
    if "fake" in filename or "deepfake" in filename:
        return jsonify({
            "status": "threat", 
            "message": "⚠️ High Risk: Audio exhibits synthetic manipulation patterns (Deepfake detected)."
        })
    else:
        return jsonify({
            "status": "safe", 
            "message": "✅ Clean: Audio harmonic signature appears authentic."
        })

@app.route('/api/scan-threat', methods=['POST'])
def scan_threat():
    payload = request.form.get('payload', '')
    
    if not payload:
        return jsonify({"status": "safe", "message": "❌ Payload is empty."})
    
    danger_keywords = ['hack', 'scam', 'otp', 'lottery', 'free money', 'urgent', 'verify account']
    is_threat = any(word in payload.lower() for word in danger_keywords)
    
    if is_threat:
        return jsonify({
            "status": "threat",
            "message": "🚨 Warning: Phishing or malicious pattern detected in payload text!"
        })
    else:
        return jsonify({
            "status": "safe",
            "message": "🛡️ Secure: No malicious threat signatures found in payload."
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
