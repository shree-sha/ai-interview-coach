import { useState } from "react";
import "./Header.css";

export default function Header({ user, onLogin, onRegister, onLogout }) {
  const [showModal, setShowModal] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (isRegister) {
        await onRegister(form.name, form.email, form.password);
      } else {
        await onLogin(form.email, form.password);
      }
      setShowModal(false);
      setForm({ name: "", email: "", password: "" });
    } catch {
      setError("Invalid credentials. Please try again.");
    }
  };

  return (
    <>
      <header className="header">
        <div className="header-brand">🎯 AI Interview Coach</div>
        <div className="header-right">
          {user ? (
            <>
              <span className="header-username">👤 {user.name}</span>
              <button className="btn-logout" onClick={onLogout}>Logout</button>
            </>
          ) : (
            <button className="btn-login-icon" onClick={() => setShowModal(true)} title="Sign In">
              <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>Sign In</span>
            </button>
          )}
        </div>
      </header>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setShowModal(false)}>✕</button>
            <h2>{isRegister ? "Create Account" : "Sign In"}</h2>
            <form onSubmit={handleSubmit}>
              {isRegister && (
                <input className="modal-input" placeholder="Full Name" value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })} required />
              )}
              <input className="modal-input" type="email" placeholder="Email" value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })} required />
              <input className="modal-input" type="password" placeholder="Password" value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })} required />
              {error && <p className="modal-error">{error}</p>}
              <button className="btn-submit" type="submit">{isRegister ? "Register" : "Login"}</button>
            </form>
            <p className="modal-toggle">
              {isRegister ? "Already have an account?" : "Don't have an account?"}
              <span onClick={() => { setIsRegister(!isRegister); setError(""); }}> {isRegister ? "Sign In" : "Register"}</span>
            </p>
          </div>
        </div>
      )}
    </>
  );
}
