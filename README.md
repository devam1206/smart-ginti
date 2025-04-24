# Smart-Ginti: Classroom Attendance Monitor

A computer vision application that processes classroom videos to count student attendance at regular intervals.

## Features

- Automated head detection using Roboflow API
- Processes videos in one-hour segments
- Captures attendance at 15, 30, 45, and 50-minute marks of each hour
- Generates visual output with bounding boxes around detected heads
- Produces a summary report of attendance counts

## Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- pip
- npm

### Backend Setup
1. Navigate to the backend directory:
```bash
cd backend
```

2. Install required Python packages:
```bash
pip install flask opencv-python requests python-dotenv pillow numpy matplotlib
```

3. Create a `.env` file with your Roboflow credentials:
```
ROBOFLOW_API_URL=your_api_url
ROBOFLOW_API_KEY=your_api_key
ROBOFLOW_MODEL_ID=your_model_id
ROBOFLOW_VERSION=your_version
```

### Frontend Setup
1. Navigate to the root directory and install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

## Usage

1. Start the Flask backend server:
```bash
cd backend
python app.py
```

2. Open the web interface in your browser
3. Upload a classroom video file
4. Wait for processing to complete
5. View the results in the output folder:
   - Annotated images for each hour
   - Text summary of head counts

## Output

The system generates:
- Annotated images showing detected heads for each hour
- A summary text file with head counts
- Visual markers showing detection boundaries

## Technical Details

- Backend: Python/Flask
- Frontend: React/Vite
- Computer Vision: OpenCV
- Head Detection: Roboflow API

## Security Note

Make sure to keep your `.env` file private and never commit it to version control.
