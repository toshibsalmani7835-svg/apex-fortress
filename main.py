import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Simple HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Apex Fortress - Deepfake Detection</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; text-align: center; padding: 50px; }
        .container { background: #161b22; padding: 30px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { color: #58a6ff; }
        input[type="file"] { margin: 20px 0; color: #c9d1d9; }
        button { background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; }
        button:hover { background: #2ea043; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Apex Fortress</h1>
        <p>Advanced Deepfake & Media Authentication Portal</p>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" required><br>
            <button type="submit">Analyze Media</button>
        </form>
        {% if filename %}
            <p style="color: #3fb950; margin-top: 20px;">File '{{ filename }}' uploaded successfully and queued for analysis!</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    uploaded_filename = None
    if request.method == "POST":
        if "file" in request.files:
            file = request.files["file"]
            if file.filename != "":
                uploaded_filename = file.filename
                # Aap yahan apna deepfake model prediction logic jod sakte hain
    return render_template_string(HTML_TEMPLATE, filename=uploaded_filename)

if __name__ == "__main__":
    app.run(host="0.0.00", port=5000, debug=True)
