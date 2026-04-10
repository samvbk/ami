








import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Convert base64 to blob
const dataURLtoBlob = (dataurl) => {
  if (!dataurl) return null;
  try {
    const arr = dataurl.split(',');
    const mime = arr[0].match(/:(.*?);/)[1];
    const bstr = atob(arr[1]);
    let n = bstr.length;
    const u8arr = new Uint8Array(n);
    while (n--) {
      u8arr[n] = bstr.charCodeAt(n);
    }
    return new Blob([u8arr], { type: mime });
  } catch (error) {
    console.error('Error converting image:', error);
    return null;
  }
};

// Main chat function
export const sendMessage = async (memberId, message, useAudio = true) => {
  try {
    console.log('💬 Sending message:', message.substring(0, 50));

    const formData = new FormData();
    formData.append('member_id', memberId.toString());
    formData.append('message', message);
    formData.append('use_voice', useAudio.toString());
    if (lat && lon) {
      formData.append('lat', lat);
      formData.append('lon', lon);
    }

    const response = await api.post('/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('✅ Response received:', response.data);

    return response.data;

  } catch (error) {
    console.error('❌ API Error:', error);

    if (error.code === 'ERR_NETWORK') {
      return {
        success: false,
        response: "I can't connect to the server. Please check if the backend is running.",
        emotion: "concerned"
      };
    }

    if (error.response) {
      console.error('Backend error:', error.response.status, error.response.data);
      return {
        success: false,
        response: `Server error: ${error.response.status}. Please try again.`,
        emotion: "concerned"
      };
    }

    return {
      success: false,
      response: "Oops! Something went wrong. Please try again.",
      emotion: "concerned"
    };
  }
};

// Face recognition
export const recognizeFace = async (imageBase64) => {
  try {
    const blob = dataURLtoBlob(imageBase64);
    if (!blob) {
      throw new Error('Failed to convert image');
    }

    const formData = new FormData();
    formData.append('image', blob, 'face.jpg');

    const response = await api.post('/recognize', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('Face recognition response:', response.data);

    if (response.data.success && response.data.recognized) {
      return {
        success: true,
        recognized: true,
        member: response.data.member,
        message: `Welcome back, ${response.data.member.name}!`
      };
    } else {
      return {
        success: true,
        recognized: false,
        message: response.data.message || 'Face not recognized. Please register.'
      };
    }

  } catch (error) {
    console.error('Face recognition error:', error);
    return {
      success: false,
      message: "Face recognition failed. Check camera permissions and backend connection."
    };
  }
};

export const registerMember = async (memberData, imageBase64) => {
  try {
    console.log('📝 Registering:', memberData.member_name);

    const blob = dataURLtoBlob(imageBase64);
    if (!blob) {
      throw new Error('Failed to convert image');
    }

    const formData = new FormData();
    formData.append('image', blob, 'face.jpg');
    formData.append('family_name', memberData.family_name || '');
    formData.append('member_name', memberData.member_name || '');
    formData.append('role', memberData.role || '');
    formData.append('age', memberData.age || '');
    formData.append('medical_history', memberData.medical_history || '');
    formData.append('emergency_contact', memberData.emergency_contact || '');

    const response = await api.post('/register', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log('Registration response:', response.data);

    if (response.data.success) {
      return {
        success: true,
        member_id: response.data.member_id,
        family_id: response.data.family_id,
        message: `Successfully registered ${memberData.member_name}`
      };
    } else {
      return {
        success: false,
        message: response.data.message || 'Registration failed.'
      };
    }

  } catch (error) {
    console.error('Registration error:', error);
    return {
      success: false,
      message: 'Registration failed. Check backend connection.'
    };
  }
};

// News API
export const getNews = async (category = "general", country = "in") => {
  try {
    const response = await api.get('/news', {
      params: { category, country }
    });
    return response.data;
  } catch (error) {
    console.error('News API error:', error);
    return { success: false, error: 'Failed to fetch news' };
  }
};

// Weather API
export const getWeather = async (city = "Delhi") => {
  try {
    const response = await api.get('/weather', {
      params: { city }
    });
    return response.data;
  } catch (error) {
    console.error('Weather API error:', error);
    return { success: false, error: 'Failed to fetch weather' };
  }
};

// Get audio file URL
export const getAudioUrl = (filename) => {
  if (!filename) return null;
  return `${API_BASE}/audio/${filename}`;
};

// Test backend connection
export const testBackend = async () => {
  try {
    const response = await api.get('/health');
    return { connected: true, data: response.data };
  } catch (error) {
    return { connected: false, error: error.message };
  }
};