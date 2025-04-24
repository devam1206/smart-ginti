const API_URL = 'http://localhost:5000'; // Change this to your Flask server URL

export const uploadVideo = async (videoFile) => {
  const formData = new FormData();
  formData.append('video', videoFile);

  try {
    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error uploading video:', error);
    throw error;
  }
};