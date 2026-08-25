import { useEffect, useState } from "react";
import "./Header.css";
import { authStrings } from "../constants/strings";
import {
  isValidEmail,
  isValidPassword,
  validateConfirmPassword,
  validateEmail,
  validatePassword,
} from "../validation/authValidation";

export default function Header({
  user,
  onLogin,
  onRegister,
  onLogout,
  isModalOpen = false,
  onCloseModal,
  defaultMode = "login",
}) {
  const [showModal, setShowModal] = useState(Boolean(isModalOpen));
  const [isRegister, setIsRegister] = useState(defaultMode === "register");
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});

  useEffect(() => {
    setShowModal(Boolean(isModalOpen));
  }, [isModalOpen]);

  useEffect(() => {
    setIsRegister(defaultMode === "register");
  }, [defaultMode]);

  const resetForm = () => {
    setForm({ name: "", email: "", password: "", confirmPassword: "" });
    setShowPassword(false);
    setShowConfirmPassword(false);
    setError("");
    setFieldErrors({});
  };

  const closeModal = () => {
    setShowModal(false);
    resetForm();
    onCloseModal?.();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const nextFieldErrors = {};
    if (!isValidEmail(form.email)) nextFieldErrors.email = authStrings.emailInvalid;
    if (!isValidPassword(form.password)) nextFieldErrors.password = authStrings.passwordTooShort;

    if (isRegister) {
      if (!form.name.trim()) {
        setError(authStrings.fullNameRequired);
        return;
      }
      if (form.password !== form.confirmPassword) {
        nextFieldErrors.confirmPassword = authStrings.passwordsDoNotMatch;
      }
    }

    if (Object.keys(nextFieldErrors).length > 0) {
      setFieldErrors(nextFieldErrors);
      return;
    }

    try {
      if (isRegister) {
        await onRegister(form.name.trim(), form.email.trim(), form.password);
      } else {
        await onLogin(form.email.trim(), form.password);
      }
      closeModal();
    } catch (err) {
      const msg = err?.response?.data?.detail || err?.message || authStrings.tryAgain;
      setError(msg.includes("already") ? authStrings.duplicateEmail : msg);
    }
  };

  return (
    <>
      <header className="header">
        <div className="header-brand">🎯 {authStrings.brand}</div>
        <div className="header-right">
          {user ? (
            <>
              <span className="header-username">👤 {user.name}</span>
              <button className="btn-logout" type="button" onClick={onLogout}>{authStrings.logout}</button>
            </>
          ) : (
            <button
              className="btn-login-icon"
              type="button"
              onClick={() => {
                setIsRegister(false);
                setShowModal(true);
                resetForm();
              }}
              title={authStrings.signInTitle}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
              <span>{authStrings.signInTitle}</span>
            </button>
          )}
        </div>
      </header>

      {showModal && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal auth-modal" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" type="button" onClick={closeModal} aria-label={authStrings.closeLoginModal}>✕</button>
            <div className="auth-header">
              <span className="auth-badge">{isRegister ? authStrings.createAccountBadge : authStrings.welcomeBackBadge}</span>
              <h2>{isRegister ? authStrings.createAccountTitle : authStrings.loginTitle}</h2>
              <p>
                {isRegister
                  ? authStrings.registrationDescription
                  : authStrings.loginDescription}
              </p>
            </div>

            <form onSubmit={handleSubmit} className="auth-form">
              {isRegister && (
                <input
                  className="modal-input"
                  placeholder={authStrings.fullName}
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  required
                />
              )}
              <input
                className="modal-input"
                type="email"
                placeholder={authStrings.email}
                value={form.email}
                onChange={(e) => {
                  const email = e.target.value;
                  setForm({ ...form, email });
                  setFieldErrors({ ...fieldErrors, email: email && validateEmail(email) ? authStrings.emailInvalid : "" });
                }}
                aria-invalid={Boolean(fieldErrors.email)}
                aria-describedby={fieldErrors.email ? "email-error" : undefined}
                required
              />
              {fieldErrors.email && <p id="email-error" className="field-error">{fieldErrors.email}</p>}
              <div className="password-field">
                <input
                  className="modal-input"
                  type={showPassword ? "text" : "password"}
                  placeholder={authStrings.password}
                  value={form.password}
                  onChange={(e) => {
                    const password = e.target.value;
                    setForm({ ...form, password });
                    setFieldErrors({
                      ...fieldErrors,
                      password: password && validatePassword(password) ? authStrings.passwordTooShort : "",
                      confirmPassword: form.confirmPassword && validateConfirmPassword(password, form.confirmPassword) ? authStrings.passwordsDoNotMatch : "",
                    });
                  }}
                  aria-invalid={Boolean(fieldErrors.password)}
                  aria-describedby={fieldErrors.password ? "password-error" : undefined}
                  required
                />
                <button
                  className="password-toggle"
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  title={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeIcon /> : <EyeOffIcon />}
                </button>
              </div>
              {fieldErrors.password && <p id="password-error" className="field-error">{fieldErrors.password}</p>}
              {isRegister && (
                <div className="password-field">
                  <input
                    className="modal-input"
                    type={showConfirmPassword ? "text" : "password"}
                    placeholder={authStrings.confirmPassword}
                    value={form.confirmPassword}
                    onChange={(e) => {
                      const confirmPassword = e.target.value;
                      setForm({ ...form, confirmPassword });
                      setFieldErrors({ ...fieldErrors, confirmPassword: confirmPassword && validateConfirmPassword(form.password, confirmPassword) ? authStrings.passwordsDoNotMatch : "" });
                    }}
                    aria-invalid={Boolean(fieldErrors.confirmPassword)}
                    aria-describedby="confirm-password-error"
                    required
                  />
                  <button
                    className="password-toggle"
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                    title={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                  >
                    {showConfirmPassword ? <EyeIcon /> : <EyeOffIcon />}
                  </button>
                </div>
              )}
              {fieldErrors.confirmPassword && <p id="confirm-password-error" className="field-error">{fieldErrors.confirmPassword}</p>}
              {error && <p className="modal-error">{error}</p>}
              <button className="btn-submit" type="submit">{isRegister ? authStrings.submitRegister : authStrings.submitLogin}</button>
            </form>

            <p className="modal-toggle">
              {isRegister ? authStrings.existingAccount : authStrings.newAccount}
              <span
                onClick={() => {
                  setIsRegister(!isRegister);
                  setError("");
                }}
              >
                {isRegister ? ` ${authStrings.signIn}` : ` ${authStrings.registerTitle}`}
              </span>
            </p>
          </div>
        </div>
      )}
    </>
  );
}

function EyeIcon() {
  return (
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7-10-7-10-7Z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="m3 3 18 18" />
      <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
      <path d="M9.9 4.2A10.5 10.5 0 0 1 12 4c6.5 0 10 8 10 8a18.5 18.5 0 0 1-3.1 4.4" />
      <path d="M6.6 6.6C3.7 8.4 2 12 2 12s3.5 8 10 8a10.5 10.5 0 0 0 3.1-.5" />
    </svg>
  );
}
