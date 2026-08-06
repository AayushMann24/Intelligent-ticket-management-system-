import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  Eye,
  EyeOff,
  Mail,
  Lock,
  ShieldCheck,
  ArrowLeft,
} from "lucide-react";

import { loginUser } from "../services/authService";

export default function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const response = await loginUser({
        email,
        password,
      });

      localStorage.setItem(
        "token",
        response.access_token
      );

      navigate("/dashboard");

    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">

      {/* Back Button */}

      <div className="p-6">

        <button
          type="button"
          onClick={() => navigate("/")}
          className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-slate-300 transition hover:bg-slate-800 hover:text-white"
        >
          <ArrowLeft size={18} />
          Back to Home
        </button>

      </div>

      {/* Login Card */}

      <div className="flex items-center justify-center px-6 pb-10">

        <form
          onSubmit={handleLogin}
          className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl"
        >

          {/* Header */}

          <div className="mb-8 text-center">

            <ShieldCheck
              size={60}
              className="mx-auto text-blue-500"
            />

            <h1 className="mt-4 text-4xl font-bold text-white">
              Welcome Back 👋
            </h1>

            <p className="mt-2 text-slate-400">
              Login to Intelligent Ticket Management System
            </p>

          </div>

          {/* Email */}

          <div className="relative mb-5">

            <Mail
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-4 text-white outline-none transition focus:border-blue-500"
            />

          </div>

          {/* Password */}

          <div className="relative mb-4">

            <Lock
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <input
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              placeholder="Password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-12 text-white outline-none transition focus:border-blue-500"
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword(!showPassword)
              }
              className="absolute right-4 top-3 text-slate-400 transition hover:text-white"
            >
              {showPassword
                ? <EyeOff size={20} />
                : <Eye size={20} />}
            </button>

          </div>

          {/* Remember + Forgot */}

          <div className="mb-5 flex items-center justify-between">

            <label className="flex items-center gap-2 text-sm text-slate-400">

              <input
                type="checkbox"
                checked={remember}
                onChange={(e) =>
                  setRemember(e.target.checked)
                }
              />

              Remember Me

            </label>

            <button
              type="button"
              onClick={() =>
                alert(
                  "Password reset is not implemented in this demo."
                )
              }
              className="text-sm text-blue-400 hover:text-blue-300"
            >
              Forgot Password?
            </button>

          </div>

          {/* Error */}

          {error && (

            <div className="mb-5 rounded-lg border border-red-600 bg-red-900/30 p-3 text-sm text-red-300">

              {error}

            </div>

          )}

          {/* Login Button */}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition duration-300 hover:scale-[1.02] hover:bg-blue-700 disabled:bg-slate-700"
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

          {/* Register */}

          <p className="mt-6 text-center text-slate-400">

            Don't have an account?

            <Link
              to="/register"
              className="ml-2 font-semibold text-blue-400 hover:text-blue-300"
            >
              Register
            </Link>

          </p>

        </form>

      </div>

    </div>
  );
}