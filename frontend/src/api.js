const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const getTokenFromCookie = () => {
  const match = document.cookie.match(new RegExp('(^| )token=([^;]+)'));
  if (match) return match[2];
  return null;
};

const clearTokenCookie = () => {
  document.cookie = "token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
};

const setTokenCookie = (token) => {
  document.cookie = `token=${token}; path=/;`;
};

const getAuthHeaders = () => {
  const token = getTokenFromCookie();
  const headers = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  return headers;
};

const handleResponse = async (response) => {
  if (response.status === 401) {
    clearTokenCookie();
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }
  return response.json();
};

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
    body: formData,
  });

  return handleResponse(response);
};

export const getNotes = async (docId) => {
  const response = await fetch(`${API_BASE_URL}/analyze/${docId}`, {
    method: "POST",
    headers: {
      ...getAuthHeaders(),
    },
  });

  return handleResponse(response);
};

export const askQuestion = async (docId, query) => {
  const response = await fetch(
    `${API_BASE_URL}/ask/${docId}?query=${encodeURIComponent(query)}`,
    {
      method: "POST",
      headers: {
        ...getAuthHeaders(),
      },
    }
  );

  return handleResponse(response);
};

export const loginUser = async (username, password) => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error("Login failed");
  }
  const data = await response.json();
  if (data.token) {
    setTokenCookie(data.token);
  }
  return data;
};

export const googleLoginAPI = async (credential) => {
  const response = await fetch(`${API_BASE_URL}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credential }),
  });

  if (!response.ok) {
    throw new Error("Google Login failed");
  }
  const data = await response.json();
  if (data.token) {
    setTokenCookie(data.token);
  }
  return data;
};

export const registerUser = async (email, password, fullName) => {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Registration failed");
  }
  return response.json();
};
