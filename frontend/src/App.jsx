import { useState } from "react";
import Header from "./Components/Header";
import InterviewCard from "./Components/InterviewCard";
import { useAuth } from "./Controllers/useAuth";
import { useInterview } from "./Controllers/useInterview";
import "./App.css";

function App() {
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState("login");
  const { user, login, register, logout } = useAuth();
  const interview = useInterview(user, {
    onRequireAuth: () => {
      setAuthMode("login");
      setAuthModalOpen(true);
    },
  });

  return (
    <div className="app-container">
      <Header
        user={user}
        onLogin={login}
        onRegister={register}
        onLogout={logout}
        isModalOpen={authModalOpen}
        onCloseModal={() => setAuthModalOpen(false)}
        defaultMode={authMode}
      />
      <InterviewCard {...interview} onRequireAuth={() => {
        setAuthMode("login");
        setAuthModalOpen(true);
      }} />
    </div>
  );
}

export default App;
