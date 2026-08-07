import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Automatically attach JWT token
api.interceptors.request.use((config) => {

  const token = localStorage.getItem("token");

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

// Handle expired sessions
api.interceptors.response.use(

  (response) => response,

  (error) => {

    if (error.response?.status === 401) {

      localStorage.clear();

      alert("Session expired. Please login again.");

      window.location.href = "/";

    }

    return Promise.reject(error);

  }

);

export default api;