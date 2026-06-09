const API_BASE = "http://127.0.0.1:8000";

export const generateQuestion = async (role) => {
  const response = await fetch(`${API_BASE}/question?role=${encodeURIComponent(role)}`);
  return await response.json();
};

export const evaluateAnswer = async (question, answer) => {
  const response = await fetch(`${API_BASE}/evaluate-answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, answer }),
  });
  return await response.json();
};
