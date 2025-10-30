# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import video_analyzer # <-- This imports your cleaned-up file!

# Initialize the Flask app
app = Flask(__name__)
CORS(app) # Allows your frontend to talk to this server

# Define a folder to temporarily store uploaded videos
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# This is your API endpoint: http://127.0.0.1:5000/analyze
@app.route('/analyze', methods=['POST'])
def handle_video_upload():
    # 1. Check if a file was sent
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    file = request.files['video']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        # 2. Save the video file temporarily
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(video_path)

        # 3. RUN YOUR ML/MEDIAPIPE ANALYSIS
        try:
            # This is where we call your other file's function
            results = video_analyzer.analyze_video(video_path)
            
            # Check if your analyzer returned an error (like "No pose detected")
            if 'error' in results:
                return jsonify(results), 400

        except Exception as e:
            # Handle any unexpected crash in your analysis code
            return jsonify({'error': f'Analysis failed: {str(e)}'}), 500
        
        finally:
            # 4. Clean up the saved video file
            if os.path.exists(video_path):
                os.remove(video_path)

        # 5. Send the successful results back to the frontend
        return jsonify(results)

# This makes the server run when you execute `python app.py`
if __name__ == '__main__':
    app.run(debug=True, port=5000) # Runs on http://127.0.0.1:5000