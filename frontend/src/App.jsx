import { useState } from "react";
import { generateQuestion } from "./services/api";

function App() {
  const [role, setRole] = useState("Python Developer");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");

  const handleGenerate = async () => {
    const data = await generateQuestion(role);
    setQuestion(data.question);
  };

  return (
    <div style={{ padding: "30px" }}>
      <h1>AI Interview Coach</h1>

      <select
        value={role}
        onChange={(e) => setRole(e.target.value)}
      >
        <option>Python Developer</option>
        <option>React Developer</option>
        <option>Data Analyst</option>
        <option>QA Engineer</option>
      </select>

      <br />
      <br />

      <button onClick={handleGenerate}>
        Generate Question
      </button>

      <br />
      <br />

      {question && (
        <>
          <h3>Question</h3>
          <div>{question}</div>

          <br />

          <textarea
            rows="6"
            cols="60"
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer..."
          />

          <br />
          <br />

          <button>
            Submit Answer
          </button>
        </>
      )}
    </div>
  );
}

export default App;