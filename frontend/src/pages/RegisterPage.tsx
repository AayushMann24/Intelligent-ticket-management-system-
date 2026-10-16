import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

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

import { useAuth } from "../context/useAuth";
import { useReducedMotion } from "../hooks/useReducedMotion";
import AnimatedBackground from "../components/common/AnimatedBackground";

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();
  const reducedMotion = useReducedMotion();

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

      await register(form);

      alert("Registration Successful!");

      navigate("/login");

    } catch {

      setError("Registration Failed.");

    } finally {

      setLoading(false);

    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[#05070f]">

      <AnimatedBackground variant="public" />

      {/* Back Button */}

      <div className="relative z-10 p-6">

        <motion.button
          type="button"
          onClick={() => navigate("/")}
          initial={reducedMotion ? undefined : { opacity: 0, x: -12 }}
          animate={reducedMotion ? undefined : { opacity: 1, x: 0 }}
          whileHover={reducedMotion ? {} : { x: -4 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
          transition={{ duration: 0.3 }}
          className="itms-glass flex items-center gap-2 rounded-lg px-4 py-2 text-slate-300 transition-colors hover:border-cyan-400/40 hover:text-white"
        >
          <ArrowLeft size={18} />
          Back to Home
        </motion.button>

      </div>

      {/* Register Card */}

      <div className="relative z-10 flex items-center justify-center px-6 pb-10">

        <motion.form
          onSubmit={handleRegister}
          initial={reducedMotion ? undefined : { opacity: 0, y: 24 }}
          animate={reducedMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="itms-glass-strong w-full max-w-md rounded-2xl p-8 shadow-2xl"
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

          <motion.button
            type="submit"
            disabled={loading}
            whileHover={reducedMotion || loading ? {} : { scale: 1.02 }}
            whileTap={reducedMotion || loading ? {} : { scale: 0.98 }}
            className="w-full rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-semibold text-white shadow-lg shadow-cyan-500/20 transition-shadow duration-300 hover:shadow-cyan-400/40 disabled:bg-slate-700 disabled:bg-none disabled:shadow-none"
          >
            {loading
              ? "Creating Account..."
              : "Register"}
          </motion.button>

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

        </motion.form>

      </div>

    </div>
  );
}