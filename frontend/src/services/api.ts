import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true, // Send cookies with cross-origin requests
});

// CSRF token management
let csrfToken: string | null = null;

function getCsrfToken(): string | null {
  // Try to get from cookie
  const cookies = document.cookie.split("; ");
  for (const cookie of cookies) {
    const [name, value] = cookie.split("=");
    if (name === "csrf_token") {
      return decodeURIComponent(value);
    }
  }
  return csrfToken;
}

function setCsrfToken(token: string) {
  csrfToken = token;
}

// Automatically attach CSRF token for state-changing requests
api.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase();
  if (method && ["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    // Skip CSRF for auth endpoints that establish cookies
    const url = config.url || "";
    if (!["/auth/login", "/auth/register", "/auth/refresh", "/auth/logout"].some(endpoint => url.includes(endpoint))) {
      const token = getCsrfToken();
      if (token) {
        config.headers["X-CSRF-Token"] = token;
      }
    }
  }
  return config;
});

// Handle CSRF token from response cookies
api.interceptors.response.use(
  (response) => {
    // Extract CSRF token from Set-Cookie header
    const setCookie = response.headers["set-cookie"];
    if (setCookie) {
      const cookies = Array.isArray(setCookie) ? setCookie : [setCookie];
      for (const cookie of cookies) {
        if (cookie.startsWith("csrf_token=")) {
          const token = cookie.split(";")[0].split("=")[1];
          if (token) {
            setCsrfToken(decodeURIComponent(token));
          }
        }
      }
    }
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Clear any stored CSRF token
      csrfToken = null;
      window.location.href = "/login?expired=1";
    } else if (error.response?.status === 403 && error.response?.data?.detail?.includes("CSRF")) {
      // CSRF failure - redirect to login
      csrfToken = null;
      window.location.href = "/login?csrf=1";
    }
    return Promise.reject(error);
  }
);

export default api;