// src/services/api.js

const API_BASE = "http://127.0.0.1:8000";

export const generateQuestion = async (role) => {
  const response = await fetch(
    `${API_BASE}/question?role=${role}`
  );

  return await response.json();
};