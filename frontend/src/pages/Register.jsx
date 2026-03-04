import { AlertCircle, CheckCircle2, Eye, EyeOff, Lock, Mail } from "lucide-react";
import { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import logo from "../assets/Logo_extracted.png";

function LiquidFrame({ children, className = "" }) {
  return (
    <div className={`liquid-frame ${className}`.trim()}>
      <span className="liquid-grid" aria-hidden="true" />
      <span className="liquid-glow" aria-hidden="true" />
      <span className="liquid-ring liquid-ring-dark" aria-hidden="true" />
      <span className="liquid-ring liquid-ring-light" aria-hidden="true" />
      <span className="liquid-ring liquid-ring-core" aria-hidden="true" />
      <div className="liquid-frame-inner">{children}</div>
    </div>
  );
}

function LiquidInput({
  type = "text",
  placeholder,
  icon,
  rightNode,
  autoComplete,
  value,
  onChange,
  name,
  id,
}) {
  return (
    <LiquidFrame>
      <div className="liquid-main">
        <span className="liquid-icon">{icon}</span>
        <input
          id={id}
          name={name}
          type={type}
          placeholder={placeholder}
          className="liquid-input"
          autoComplete={autoComplete}
          value={value}
          onChange={onChange}
          required
        />
        {rightNode ? <span className="liquid-right">{rightNode}</span> : null}
      </div>
    </LiquidFrame>
  );
}

export default function Register() {
  const navigate = useNavigate();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [apiReachable, setApiReachable] = useState(null);

  const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
  const apiRootUrl = rawApiBaseUrl.endsWith("/api/v1")
    ? rawApiBaseUrl.replace(/\/api\/v1$/, "")
    : rawApiBaseUrl;
  const authApiBaseUrl = rawApiBaseUrl.endsWith("/api/v1") ? rawApiBaseUrl : `${rawApiBaseUrl}/api/v1`;

  useEffect(() => {
    let isMounted = true;

    async function checkApi() {
      try {
        await axios.get(`${apiRootUrl}/health`, { timeout: 3500 });
        if (isMounted) setApiReachable(true);
      } catch {
        if (isMounted) setApiReachable(false);
      }
    }

    checkApi();
    return () => {
      isMounted = false;
    };
  }, [apiRootUrl]);

  async function handleSubmit(event) {
    event.preventDefault();
    setErrorMessage("");
    setSuccessMessage("");

    if (!email.trim()) {
      setErrorMessage("Please enter your email.");
      return;
    }
    if (password.length < 8) {
      setErrorMessage("Password must be at least 8 characters.");
      return;
    }
    if (password !== confirmPassword) {
      setErrorMessage("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);

    try {
      await axios.post(
        `${authApiBaseUrl}/auth/register`,
        {
          email: email.trim(),
          password,
        },
        { timeout: 10000 }
      );
      setSuccessMessage("Account created. Redirecting to sign in...");
      setTimeout(() => {
        navigate("/login", {
          replace: true,
          state: { registrationSuccess: `Account created for ${email.trim()}. Please sign in.` },
        });
      }, 850);
    } catch (error) {
      if (error?.response?.status === 409) {
        setErrorMessage("An account with this email already exists.");
      } else if (error?.response?.status === 422) {
        setErrorMessage("Please enter a valid email and at least 8-character password.");
      } else if (error?.code === "ECONNABORTED") {
        setErrorMessage("Request timed out. Please try again.");
      } else if (!error?.response) {
        setErrorMessage(
          `Can't reach API at ${authApiBaseUrl}. Start backend or set VITE_API_BASE_URL in frontend/.env.`
        );
      } else {
        setErrorMessage("Unable to create account right now. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="login-scene relative isolate min-h-screen overflow-hidden text-white">
      <div className="absolute inset-0 login-bg-gradient" />
      <div className="absolute -left-20 top-10 h-96 w-96 rounded-full login-orb-one login-float-slow" />
      <div className="absolute -right-16 bottom-10 h-[26rem] w-[26rem] rounded-full login-orb-two login-float-fast" />
      <div className="absolute inset-0 grain" />

      <main className="relative z-10 mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-5 py-12 md:px-8">
        <div className="login-brand-corner">
          <img src={logo} alt="AreWeGoing logo" className="corner-logo" />
        </div>

        <section className="login-panel login-reveal flex w-full max-w-5xl flex-col gap-10 rounded-[2.2rem] border border-[#ece6d9]/45 p-7 text-[#f8f6f1] shadow-glass md:flex-row md:items-center md:justify-between md:gap-12 md:p-10">
          <div className="flex max-w-md flex-col items-start justify-center">
            <h1 className="mt-7 text-4xl leading-[0.95] tracking-tight md:text-6xl">
              Your trip begins,
              <br />
              right here.
            </h1>
            <p className="mt-4 text-sm text-[#ece6d9]/85 md:text-base">
              Create your AreWeGoing account and start planning with your people.
            </p>
          </div>

          <form className="flex w-full max-w-md flex-col gap-5" onSubmit={handleSubmit}>
            {apiReachable === false ? (
              <div className="feedback-banner feedback-error" role="alert" aria-live="polite">
                <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
                <p>Backend offline at {apiRootUrl}</p>
              </div>
            ) : null}

            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-[0.18em] text-[#ece6d9]/78">Email</span>
              <LiquidInput
                id="register-email"
                name="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errorMessage) setErrorMessage("");
                }}
                icon={<Mail className="h-4 w-4 text-[#ece6d9]/85" aria-hidden="true" />}
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-[0.18em] text-[#ece6d9]/78">Password</span>
              <LiquidInput
                id="register-password"
                name="password"
                type={showPassword ? "text" : "password"}
                placeholder="At least 8 characters"
                autoComplete="new-password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (errorMessage) setErrorMessage("");
                }}
                icon={<Lock className="h-4 w-4 text-[#ece6d9]/85" aria-hidden="true" />}
                rightNode={
                  <button
                    type="button"
                    className="text-[#ece6d9]/75 transition hover:text-[#f8f6f1]"
                    onClick={() => setShowPassword((prev) => !prev)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                }
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-[0.18em] text-[#ece6d9]/78">
                Confirm Password
              </span>
              <LiquidInput
                id="register-confirm-password"
                name="confirm-password"
                type={showConfirmPassword ? "text" : "password"}
                placeholder="Re-enter password"
                autoComplete="new-password"
                value={confirmPassword}
                onChange={(e) => {
                  setConfirmPassword(e.target.value);
                  if (errorMessage) setErrorMessage("");
                }}
                icon={<Lock className="h-4 w-4 text-[#ece6d9]/85" aria-hidden="true" />}
                rightNode={
                  <button
                    type="button"
                    className="text-[#ece6d9]/75 transition hover:text-[#f8f6f1]"
                    onClick={() => setShowConfirmPassword((prev) => !prev)}
                    aria-label={showConfirmPassword ? "Hide confirm password" : "Show confirm password"}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                }
              />
            </label>

            <LiquidFrame>
              <button type="submit" className="liquid-button" disabled={isSubmitting}>
                {isSubmitting ? "Creating account..." : "Create Account"}
              </button>
            </LiquidFrame>

            {errorMessage ? (
              <div className="feedback-banner feedback-error" role="alert" aria-live="polite">
                <AlertCircle className="h-4 w-4 shrink-0" aria-hidden="true" />
                <p>{errorMessage}</p>
              </div>
            ) : null}
            {successMessage ? (
              <div className="feedback-banner feedback-success" role="status" aria-live="polite">
                <CheckCircle2 className="h-4 w-4 shrink-0" aria-hidden="true" />
                <p>{successMessage}</p>
              </div>
            ) : null}

            <p className="text-center text-sm text-[#ece6d9]/78">
              Already have an account?{" "}
              <button
                type="button"
                className="login-text-link text-[#fcfaf5] transition hover:text-white"
                onClick={() => navigate("/login")}
              >
                Sign in
              </button>
            </p>
          </form>
        </section>
      </main>
    </div>
  );
}
