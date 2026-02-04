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
