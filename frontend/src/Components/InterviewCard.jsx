const ROLES = ["Python Developer", "React Developer", "Data Analyst", "QA Engineer"];

const parseScore = (text) => {
  const match = text?.match(/Score:\s*(\d+)/i);
  return match ? parseInt(match[1]) : null;
};

export default function InterviewCard({ role, question, answer, evaluation, loading, evaluating, setAnswer, handleRoleChange, handleGenerate, handleSubmit }) {
  const score = parseScore(evaluation);
  const scoreColor = score >= 75 ? "#22c55e" : score >= 40 ? "#f59e0b" : "#ef4444";

  return (
    <div className="card">
      <p className="subtitle">Practice technical interviews with AI-powered feedback</p>

      <div className="field">
        <label className="label">Select Role</label>
        <select className="select" value={role} onChange={handleRoleChange}>
          {ROLES.map((r) => <option key={r}>{r}</option>)}
        </select>
      </div>

      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? "⏳ Generating..." : "⚡ Generate Question"}
      </button>

      {question && (
        <>
          <div className="question-box">
            <span className="question-label">Question</span>
            <p className="question-text">{question}</p>
          </div>
          <div className="field">
            <label className="label">Your Answer</label>
            <textarea className="textarea" value={answer} onChange={(e) => setAnswer(e.target.value)} placeholder="Type your answer here..." />
          </div>
          <button className="btn btn-success" onClick={handleSubmit} disabled={evaluating}>
            {evaluating ? "⏳ Evaluating..." : "✅ Submit Answer"}
          </button>
        </>
      )}

      {evaluation && (
        <div className="evaluation-box">
          <h3 className="eval-title">📊 Evaluation Result</h3>
          {score !== null && (
            <div className="score-wrapper">
              <div className="score-circle" style={{ borderColor: scoreColor, color: scoreColor }}>{score}%</div>
            </div>
          )}
          <p className="eval-text">{evaluation}</p>
        </div>
      )}
    </div>
  );
}
