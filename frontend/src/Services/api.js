const API_BASE = "http://127.0.0.1:8000";

export const generateQuestion = async (role) => {
  const res = await fetch(`${API_BASE}/question?role=${encodeURIComponent(role)}`);
  return res.json();
};

export const evaluateAnswer = async (question, answer, metadata, userId) => {
  const res = await fetch(`${API_BASE}/evaluate-answer`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-User-Id": String(userId) },
    body: JSON.stringify({ question, answer, ...metadata }),
  });
  if (!res.ok) throw new Error("Evaluation failed");
  return res.json();
};

export const loginUser = async (email, password) => {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Login failed");
  }
  return res.json();
};

export const registerUser = async (name, email, password) => {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw new Error(error.detail || "Registration failed");
  }
  return res.json();
};
