          async function scanVoiceAIAPI() {
            const fileInput = document.getElementById('audioInput');
            const box = document.getElementById('resultBox');
            if(!fileInput.files || fileInput.files.length === 0) { showToast("⚠️ Load audio sample first!", "error"); return; }
            
            const audioFile = fileInput.files[0];
            box.classList.remove('hidden');
            box.className = "p-2.5 rounded-xl border bg-slate-900 border-slate-700 text-yellow-300";
            document.getElementById('resultText').innerText = "🔄 Uploading audio to Railway backend...";

            const formData = new FormData();
            formData.append('file', audioFile);

            try {
                const res = await fetch(`${BACKEND_URL}/api/v1/scan-voice`, {
                    method: 'POST',
                    body: formData
                });

                if(res.ok) {
                    const data = await res.json();
                    scansCount++;
                    if(data.is_deepfake) {
                        threatsCount++;
                        box.className = "p-2.5 rounded-xl border bg-rose-950/80 border-rose-800 text-rose-200 threat-pulse";
                        document.getElementById('resultText').innerText = `⚠️ AI DEEPFAKE DETECTED: ${data.message}`;
                    } else {
                        box.className = "p-2.5 rounded-xl border bg-emerald-950/80 border-emerald-800 text-emerald-200";
                        document.getElementById('resultText').innerText = `✅ GENUINE VOICE: ${data.message}`;
                    }
                    updateStats();
                    return;
                } else {
                    // Agar server ne error diya toh error code screen par dikhao
                    const errData = await res.text();
                    box.className = "p-2.5 rounded-xl border bg-rose-950/80 border-rose-800 text-rose-200";
                    document.getElementById('resultText').innerText = `❌ Server Error (${res.status}): ${errData}`;
                }
            } catch(err) {
                // Agar internet ya connection fail hua toh yahan dikhega
                box.className = "p-2.5 rounded-xl border bg-rose-950/80 border-rose-800 text-rose-200";
                document.getElementById('resultText').innerText = `❌ Connection Failed: ${err.message}. (Railway server shyd sleep mode me ho ya offline ho)`;
            }
        }
      
