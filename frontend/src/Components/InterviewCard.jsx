const ROLES = ["Python Developer", "React Developer", "Data Analyst", "QA Engineer"];

const scoreState = (score) => {
  if (score >= 75) return "strong";
  if (score >= 40) return "developing";
  return "needs-work";
};

const confidenceLabel = (confidence) => {
  const value = String(confidence || "").toLowerCase();
  return ["low", "medium", "high"].includes(value) ? value : "not rated";
};

function FeedbackList({ title, items, type }) {
  return (
    <section className={`feedback-section feedback-section-${type}`} aria-labelledby={`${type}-title`}>
      <div className="feedback-section-heading">
        <span className="feedback-section-icon" aria-hidden="true">{type === "strengths" ? "✓" : "↗"}</span>
        <h4 id={`${type}-title`}>{title}</h4>
      </div>
      {items?.length ? (
        <ul className="feedback-list">
          {items.map((item, index) => (
            <li key={`${type}-${index}`}>
              <span className="feedback-item-marker" aria-hidden="true">{type === "strengths" ? "✓" : "→"}</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="feedback-empty">
          {type === "strengths" ? "No strengths were identified." : "No feedback was provided for this area."}
        </p>
      )}
    </section>
  );
}

export default function InterviewCard({ role, question, answer, evaluation, loading, evaluating, setAnswer, handleRoleChange, handleGenerate, handleSubmit }) {
  const feedback = evaluation?.evaluation ?? evaluation;
  const score = Number.isFinite(Number(feedback?.score)) ? Math.max(0, Math.min(100, Number(feedback.score))) : null;
  const state = score === null ? "unrated" : scoreState(score);
  const confidence = confidenceLabel(feedback?.confidence);
  const activeSegments = score === null ? 0 : Math.ceil(score / 10);

  return (
    <main className="card">
      <p className="subtitle">Practice technical interviews with AI-powered feedback</p>

      <div className="field">
        <label className="label" htmlFor="role">Select Role</label>
        <select id="role" className="select" value={role} onChange={handleRoleChange}>
          {ROLES.map((r) => <option key={r}>{r}</option>)}
        </select>
      </div>

      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate Question"}
      </button>

      {question && (
        <>
          <section className="question-box" aria-labelledby="question-title">
            <span id="question-title" className="question-label">Question</span>
            <p className="question-text">{question}</p>
          </section>
          <div className="field">
            <label className="label" htmlFor="answer">Your Answer</label>
            <textarea id="answer" className="textarea" value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Type your answer here..." />
          </div>
          <button className="btn btn-success" onClick={handleSubmit} disabled={evaluating}>
            {evaluating ? "Evaluating..." : "Submit Answer"}
          </button>
        </>
      )}

      {feedback && (
        <section className="evaluation-box" aria-labelledby="evaluation-title">
          <header className="evaluation-header">
            <div className="evaluation-intro">
              <p className="eyebrow">Coach assessment</p>
              <h3 id="evaluation-title" className="eval-title">Evaluation Result</h3>
            </div>
            <div className={`coach-assessment score-${state}`} aria-label={score === null ? "Score not available" : `Overall score: ${score} out of 100`}>
              <div className="assessment-score">
                <span className="score-value">{score === null ? "—" : score}</span>
                <span className="score-total">/100</span>
              </div>
              <div className="assessment-detail">
                <span className="assessment-label">Overall readiness</span>
                <div className="score-segments" aria-hidden="true">
                  {Array.from({ length: 10 }, (_, index) => <span key={index} className={index < activeSegments ? "is-active" : ""} />)}
                </div>
              </div>
              <span className={`confidence-badge confidence-${confidence.replace(" ", "-")}`}>{confidence} confidence</span>
            </div>
          </header>

          <div className="feedback-grid">
            <FeedbackList title="Strengths" items={feedback.strengths} type="strengths" />
            <FeedbackList title="Areas to Improve" items={feedback.improvements} type="improvements" />
          </div>

          <section className="ideal-answer" aria-labelledby="ideal-answer-title">
            <div className="ideal-answer-heading">
              <span aria-hidden="true">✦</span>
              <h4 id="ideal-answer-title">Ideal Answer</h4>
            </div>
            <p>{feedback.ideal_answer || "An ideal answer was not provided for this response."}</p>
          </section>
        </section>
      )}
    </main>
  );
}
