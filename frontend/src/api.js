const API_BASE_URL = "http://localhost:8000";

export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Failed to upload file");
  }

  return response.json();
};

export const getNotes = async (docId) => {
  const response = await fetch(`${API_BASE_URL}/analyze/${docId}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error("Failed to generate notes");
  }

  return response.json();
};

export const askQuestion = async (docId, query) => {
  const response = await fetch(
    `${API_BASE_URL}/ask/${docId}?query=${encodeURIComponent(query)}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    throw new Error("Failed to get answer");
  }

  return response.json();
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
  return response.json();
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
  return response.json();
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
