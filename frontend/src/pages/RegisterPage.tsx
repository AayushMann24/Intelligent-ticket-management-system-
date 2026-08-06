import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
  User,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  ArrowLeft,
  Briefcase,
} from "lucide-react";

import { registerUser } from "../services/authService";

export default function RegisterPage() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    role: "Employee",
  });

  const [showPassword, setShowPassword] =
    useState(false);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement
    >
  ) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegister = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {

      await registerUser(form);

      alert("Registration Successful!");

      navigate("/login");

    } catch {

      setError("Registration Failed.");

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

      {/* Register Card */}

      <div className="flex items-center justify-center px-6 pb-10">

        <form
          onSubmit={handleRegister}
          className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 shadow-2xl"
        >

          {/* Header */}

          <div className="mb-8 text-center">

            <ShieldCheck
              size={60}
              className="mx-auto text-blue-500"
            />

            <h1 className="mt-4 text-4xl font-bold text-white">
              Create Account
            </h1>

            <p className="mt-2 text-slate-400">
              Join Intelligent Ticket Management System
            </p>

          </div>

          {/* Name */}

          <div className="relative mb-5">

            <User
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <input
              name="name"
              placeholder="Full Name"
              value={form.name}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-4 text-white outline-none transition focus:border-blue-500"
            />

          </div>

          {/* Email */}

          <div className="relative mb-5">

            <Mail
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <input
              name="email"
              type="email"
              placeholder="Email Address"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-4 text-white outline-none transition focus:border-blue-500"
            />

          </div>

          {/* Password */}

          <div className="relative mb-5">

            <Lock
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <input
              name="password"
              type={
                showPassword
                  ? "text"
                  : "password"
              }
              placeholder="Password"
              value={form.password}
              onChange={handleChange}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-12 text-white outline-none transition focus:border-blue-500"
            />

            <button
              type="button"
              onClick={() =>
                setShowPassword(!showPassword)
              }
              className="absolute right-4 top-3 text-slate-400 hover:text-white"
            >
              {showPassword
                ? <EyeOff size={20} />
                : <Eye size={20} />}
            </button>

          </div>

          {/* Role */}

          <div className="relative mb-6">

            <Briefcase
              size={18}
              className="absolute left-4 top-4 text-slate-400"
            />

            <select
              name="role"
              value={form.role}
              onChange={handleChange}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-4 text-white outline-none focus:border-blue-500"
            >
              <option>Employee</option>
              <option>Technician</option>
              <option>Admin</option>
            </select>

          </div>

          {/* Error */}

          {error && (

            <div className="mb-5 rounded-lg border border-red-600 bg-red-900/30 p-3 text-sm text-red-300">

              {error}

            </div>

          )}

          {/* Register */}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-blue-600 py-3 font-semibold text-white transition duration-300 hover:scale-[1.02] hover:bg-blue-700 disabled:bg-slate-700"
          >
            {loading
              ? "Creating Account..."
              : "Register"}
          </button>

          {/* Login */}

          <p className="mt-6 text-center text-slate-400">

            Already have an account?

            <Link
              to="/login"
              className="ml-2 font-semibold text-blue-400 hover:text-blue-300"
            >
              Login
            </Link>

          </p>

        </form>

      </div>

    </div>
  );
}