import { useCallback, useEffect, useState } from "react";
import { generateQuestion, evaluateAnswer } from "../Services/api";

const TOTAL_QUESTIONS = 15;

const difficultyFor = (questionNumber) => {
  if (questionNumber <= 10) return "Easy";
  if (questionNumber <= 13) return "Medium";
  return "Hard";
};

export function useInterview(user, options = {}) {
  const { onRequireAuth } = options;
  const [role, setRole] = useState("Python Developer");
  const [topic, setTopic] = useState("General");
  const [difficulty, setDifficulty] = useState("Easy");
  const [questionNumber, setQuestionNumber] = useState(1);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [skippedCount, setSkippedCount] = useState(0);
  const [assessmentComplete, setAssessmentComplete] = useState(false);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [skipping, setSkipping] = useState(false);

  const loadQuestion = useCallback(async (nextQuestionNumber) => {
    setLoading(true);
    setEvaluation(null);
    setAnswer("");
    try {
      const data = await generateQuestion(role, nextQuestionNumber, difficultyFor(nextQuestionNumber));
      setQuestion(data.question);
      setQuestionNumber(nextQuestionNumber);
      setTopic(data.topic ?? "General");
      setDifficulty(data.difficulty ?? difficultyFor(nextQuestionNumber));
    } catch {
      alert("Failed to generate question. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [role]);

  useEffect(() => {
    queueMicrotask(() => loadQuestion(1));
  }, [loadQuestion]);

  const handleRoleChange = (e) => {
    const selectedRole = e.target.value;
    setRole(selectedRole);
    setQuestionNumber(1);
    setAnsweredCount(0);
    setSkippedCount(0);
    setAssessmentComplete(false);
  };

  const handleGenerate = async () => {
    setAnsweredCount(0);
    setSkippedCount(0);
    setAssessmentComplete(false);
    await loadQuestion(1);
  };

  const handleSubmit = async () => {
    if (!answer.trim()) return alert("Please write your answer first.");
    if (!user?.id) {
      alert("Please log in first to save your learning progress, track your practice, and receive personalized feedback.");
      onRequireAuth?.();
      return;
    }
    setEvaluating(true);
    try {
      const data = await evaluateAnswer(question, answer, { role, topic, difficulty }, user.id);
      setAnsweredCount((count) => count + 1);
      if (questionNumber === TOTAL_QUESTIONS) {
        setEvaluation(data.evaluation);
        setAssessmentComplete(true);
      } else {
        await loadQuestion(questionNumber + 1);
      }
    } catch {
      alert("Failed to evaluate answer.");
    } finally {
      setEvaluating(false);
    }
  };

  const handleSkip = async () => {
    if (evaluation || assessmentComplete) return;
    setSkippedCount((count) => count + 1);
    if (questionNumber === TOTAL_QUESTIONS) {
      setQuestion("");
      setAssessmentComplete(true);
      return;
    }
    setSkipping(true);
    try {
      await loadQuestion(questionNumber + 1);
    } finally {
      setSkipping(false);
    }
  };

  const handleNextQuestion = () => {
    if (!evaluation || questionNumber === TOTAL_QUESTIONS) return;
    loadQuestion(questionNumber + 1);
  };

  const remainingCount = TOTAL_QUESTIONS - answeredCount - skippedCount;

  return {
    role, question, answer, evaluation, loading, evaluating, difficulty,
    questionNumber, answeredCount, skippedCount, remainingCount,
    assessmentComplete, skipping, setAnswer, handleRoleChange, handleGenerate,
    handleSubmit, handleSkip, handleNextQuestion,
  };
}
