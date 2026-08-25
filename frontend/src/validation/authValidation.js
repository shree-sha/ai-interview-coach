export const isValidEmail = (email) =>
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim());

export const isValidPassword = (password) => password.length >= 8;

export const validateEmail = (email) => (isValidEmail(email) ? "" : "email");

export const validatePassword = (password) =>
  isValidPassword(password) ? "" : "password";

export const validateConfirmPassword = (password, confirmPassword) =>
  password === confirmPassword ? "" : "confirmPassword";