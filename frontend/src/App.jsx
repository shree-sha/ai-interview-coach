import Header from "./Components/Header";
import InterviewCard from "./Components/InterviewCard";
import { useAuth } from "./Controllers/useAuth";
import { useInterview } from "./Controllers/useInterview";
import "./App.css";

function App() {
  const { user, login, register, logout } = useAuth();
  const interview = useInterview();

  return (
    <div className="app-container">
      <Header user={user} onLogin={login} onRegister={register} onLogout={logout} />
      <InterviewCard {...interview} />
    </div>
  );
}

export default App;
