// Frontend API Service
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling
apiClient.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const apiService = {
  // Data Endpoints
  loadData: () => apiClient.get('/load_data'),
  
  getCourses: () => apiClient.get('/courses'),
  
  // Scheduling Endpoints
  generateTimetables: (courseIds, slotPreferences = {}) => 
    apiClient.post('/generate', {
      course_codes: courseIds,
      slot_preferences: slotPreferences,
    }),
  
  // NLP Filtering
  filterTimetables: (timetables, constraintText) =>
    apiClient.post('/filter', {
      schedules: timetables,
      constraint_text: constraintText,
    }),
  
  // System Stats
  getStats: () => apiClient.get('/stats'),
  
  // File Upload
  uploadCSV: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/upload_csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default apiService;
