import tkinter as tk
from tkinter import filedialog
import cv2
import os
from dotenv import load_dotenv
import requests
import io
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Load environment variables
load_dotenv()

API_URL = os.getenv('ROBOFLOW_API_URL')
API_KEY = os.getenv('ROBOFLOW_API_KEY')
MODEL_ID = os.getenv('ROBOFLOW_MODEL_ID')
VERSION = os.getenv('ROBOFLOW_VERSION')
CONFIDENCE = 0.5
MAX_OVERLAP = 0.3

def detect_heads(image):
    """Send the frame to Roboflow API for head detection."""
    api_url = f"{API_URL}/{MODEL_ID}/{VERSION}?api_key={API_KEY}&format=json&confidence={CONFIDENCE}&overlap={MAX_OVERLAP}"

    _, img_encoded = cv2.imencode(".jpg", image)
    response = requests.post(api_url, files={"file": img_encoded.tobytes()})

    if response.status_code == 200:
        results = response.json()
        heads = []
        for prediction in results.get("predictions", []):
            x, y, width, height = (
                prediction["x"], prediction["y"], prediction["width"], prediction["height"]
            )
            x1, y1 = int(x - width / 2), int(y - height / 2)
            x2, y2 = int(x + width / 2), int(y + height / 2)
            heads.append([x1, y1, x2, y2])
        return heads
    else:
        print("Error:", response.status_code, response.text)
        return []

def clear_output_directory(directory):
    """Clear all files in the output directory."""
    if os.path.exists(directory):
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(f"Error: {e}")

def process_video(file_path):
    print("\n=== Starting Video Processing ===")
    cap = cv2.VideoCapture(file_path)

    if not cap.isOpened():
        print("Error: Couldn't open video file.")
        return

    print("✓ Successfully opened video file")
    output_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(output_dir, exist_ok=True)
    clear_output_directory(output_dir)
    print("✓ Cleared output directory")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration_sec = total_frames / fps
    print(f"✓ Video Info - Frames: {total_frames}, FPS: {fps:.2f}, Duration: {duration_sec/60:.2f} minutes")

    head_counts = []

    # Check at 15, 30, 45, and 50 minutes for each hour
    minute_offsets = [15, 30, 45, 50]  # minutes within each hour
    
    for hour in range(8):
        print(f"\nProcessing Hour {hour + 1}...")
        max_count = 0
        best_frame = None
        best_bbox_frame = None
        
        for minute in minute_offsets:
            # Calculate frame number for this specific time
            time_in_seconds = (hour * 3600) + (minute * 60)  # convert to seconds
            frame_number = int(fps * time_in_seconds)
            
            if frame_number >= total_frames:
                continue

            print(f"  Analyzing {minute}-minute mark...", end=' ')
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                print("Failed")
                continue

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            heads = detect_heads(rgb_image)
            count = len(heads)
            print(f"Found {count} heads")

            if count > max_count:
                max_count = count
                best_frame = frame.copy()
                best_bbox_frame = frame.copy()
                for x1, y1, x2, y2 in heads:
                    cv2.rectangle(best_bbox_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if best_bbox_frame is not None:
            image_filename = os.path.join(output_dir, f"hour_{hour + 1}_heads_{max_count}.jpg")
            cv2.imwrite(image_filename, best_bbox_frame)
            print(f"✓ Hour {hour + 1} Complete - Max Count: {max_count}")

        head_counts.append((hour + 1, max_count))

    cap.release()
    print("\n✓ Video processing complete")

    # Save headcounts to a text file
    text_output_path = os.path.join(output_dir, "headcount_summary.txt")
    with open(text_output_path, "w") as f:
        for hour, count in head_counts:
            f.write(f"Hour {hour}: {count} heads detected\n")
    
    print("✓ Summary saved to file")
    print("=== Processing Complete! ===\n")

def open_file():
    """Opens a file dialog to select a video."""
    file_path = filedialog.askopenfilename(
        title="Select a Video File",
        filetypes=(("Video Files", "*.mp4;*.avi;*.mov;*.mkv"), ("All Files", "*.*"))
    )
    
    if file_path:  
        print(f"Selected File: {file_path}")  # Replaced label.config with print
        process_video(file_path)
    else:
        print("No file selected")  # Replaced label.config with print

# Flask Setup
app = Flask(__name__)
CORS(app, origins=["*"], methods=["GET", "POST", "OPTIONS"])

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/process-video', methods=['POST'])
def process_video_endpoint():
    """Endpoint to process video file uploaded from React."""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    file_path = os.path.join(os.getcwd(), file.filename)
    file.save(file_path)

    try:
        process_video(file_path)

        # Read the headcount summary text file
        output_dir = os.path.join(os.getcwd(), "output")
        text_output_path = os.path.join(output_dir, "headcount_summary.txt")
        with open(text_output_path, "r") as f:
            summary = f.read()

        # Get list of image files
        image_files = {}
        for file in os.listdir(output_dir):
            if file.startswith("hour_") and file.endswith(".jpg"):
                hour = int(file.split("_")[1])
                image_files[hour] = file

        return jsonify({
            "message": "Processing complete!", 
            "summary": summary,
            "images": image_files
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(file_path)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('output', filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)