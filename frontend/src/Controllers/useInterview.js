import { useState } from "react";
import { generateQuestion, evaluateAnswer } from "../Services/api";

export function useInterview() {
  const [role, setRole] = useState("Python Developer");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);

  const handleRoleChange = (e) => {
    setRole(e.target.value);
    setQuestion("");
    setAnswer("");
    setEvaluation(null);
  };

  const handleGenerate = async () => {
    setLoading(true);
    setEvaluation(null);
    setAnswer("");
    try {
      const data = await generateQuestion(role);
      setQuestion(data.question);
    } catch {
      alert("Failed to generate question. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!answer.trim()) return alert("Please write your answer first.");
    setEvaluating(true);
    try {
      const data = await evaluateAnswer(question, answer);
      setEvaluation(data.evaluation);
    } catch {
      alert("Failed to evaluate answer.");
    } finally {
      setEvaluating(false);
    }
  };

  return { role, question, answer, evaluation, loading, evaluating, setAnswer, handleRoleChange, handleGenerate, handleSubmit };
}
