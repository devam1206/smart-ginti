import { useState } from 'react'
import axios from 'axios'

const API_URL = '/api'  // Changed to use relative path

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [attendance, setAttendance] = useState(null)
  const [error, setError] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)

  const parseSummary = (summary) => {
    if (!summary) return [];
    return summary.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const [hour, count] = line.split(':');
        return {
          hour: hour.trim(),
          count: parseInt(count.split(' ')[1])
        };
      });
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setError(null);
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a video file')
      return
    }

    const formData = new FormData()
    formData.append('file', file)

    try {
      setLoading(true)
      const response = await axios.post(`${API_URL}/process-video`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        }
      })
      setAttendance(response.data)
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to process video. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRowClick = (hour) => {
    if (attendance?.images?.[hour]) {
      setSelectedImage(`${API_URL}/images/${attendance.images[hour]}`);
    }
  };

  return (
    <div className="grid place-items-center min-h-screen bg-gray-100 dark:bg-gray-900">
      <main className="w-[min(90%,800px)] bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
        <h1 className="text-2xl font-bold mb-4 text-gray-800 dark:text-white text-center">SmartGinti: Smart Attendance System</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6">
            <input
              type="file"
              accept="video/*"
              onChange={handleFileChange}
              className="w-full text-gray-900 dark:text-white"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading || !file}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 disabled:bg-gray-400"
          >
            {loading ? 'Processing...' : 'Calculate Attendance'}
          </button>
        </form>

        {error && (
          <div className="mt-4 text-red-500 dark:text-red-400">
            {error}
          </div>
        )}

        {attendance && (
          <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2 text-center dark:text-white">Attendance Results:</h2>
            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
              <p className="mb-4 text-green-600 dark:text-green-400 text-center">{attendance.message}</p>
              <div className="flex justify-center items-center">
                <div className="w-full max-w-lg mx-auto">
                  <table className="w-full border-2 border-black dark:border-gray-600">
                    <thead>
                      <tr className="bg-gray-200 dark:bg-gray-600">
                        <th className="px-4 py-2 text-center dark:text-white border border-black dark:border-gray-500">Time Period</th>
                        <th className="px-4 py-2 text-center dark:text-white border border-black dark:border-gray-500">Students Present</th>
                      </tr>
                    </thead>
                    <tbody>
                      {parseSummary(attendance.summary).map((row, index) => (
                        <tr 
                          key={index} 
                          className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-700'} cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-600`}
                          onClick={() => handleRowClick(row.hour.split(' ')[1])}
                        >
                          <td className="px-4 py-2 text-center text-black dark:text-white border border-black dark:border-gray-600">{row.hour}</td>
                          <td className="px-4 py-2 text-center text-black dark:text-white border border-black dark:border-gray-600">{row.count}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Image Preview Modal */}
        {selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4" onClick={() => setSelectedImage(null)}>
            <div className="relative max-w-4xl w-full">
              <img src={selectedImage} alt="Preview" className="w-full h-auto rounded-lg" />
              <button 
                className="absolute top-2 right-2 bg-white rounded-full p-2"
                onClick={(e) => {
                  e.stopPropagation();
                  setSelectedImage(null);
                }}
              >
                ✕
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
