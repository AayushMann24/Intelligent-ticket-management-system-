import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, EyeOff, Mail, Lock, ShieldCheck, ArrowLeft } from "lucide-react";

import { useAuth } from "../context/useAuth";
import { useReducedMotion } from "../hooks/useReducedMotion";
import AnimatedBackground from "../components/common/AnimatedBackground";

export default function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const reducedMotion = useReducedMotion();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [remember, setRemember] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const from = (location.state as { from?: Location })?.from?.pathname || "/dashboard";

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    initial: { opacity: 0 },
    animate: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.2 } },
  };

  const itemVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.4, ease: "easeOut" },
  };

  return (
    <motion.div
      className="relative min-h-screen overflow-hidden bg-[#05070f]"
      initial="initial"
      animate="animate"
      variants={containerVariants}
    >
      <AnimatedBackground variant="public" />

      {/* Back Button */}
      <motion.div className="p-6" variants={itemVariants}>
        <motion.button
          type="button"
          onClick={() => navigate("/")}
          className="itms-glass flex items-center gap-2 rounded-lg px-4 py-2 text-slate-300 transition-colors hover:border-cyan-400/40 hover:text-white"
          whileHover={reducedMotion ? {} : { x: -4 }}
          whileTap={reducedMotion ? {} : { scale: 0.98 }}
        >
          <ArrowLeft size={18} />
          Back to Home
        </motion.button>
      </motion.div>

      {/* Login Card */}
      <motion.div className="relative z-10 flex items-center justify-center px-6 pb-10" variants={itemVariants}>
        <motion.form
          onSubmit={handleLogin}
          className="itms-glass-strong w-full max-w-md rounded-2xl p-8 shadow-2xl"
          variants={containerVariants}
          initial="initial"
          animate="animate"
        >
          {/* Header */}
          <motion.div className="mb-8 text-center" variants={itemVariants}>
            <motion.div
              className="mx-auto text-blue-500"
              initial={{ opacity: 0, scale: 0.8, rotate: -10 }}
              animate={{ opacity: 1, scale: 1, rotate: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
            >
              <ShieldCheck size={60} />
            </motion.div>

            <motion.h1
              className="mt-4 text-4xl font-bold text-white"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.1 }}
            >
              Welcome Back 👋
            </motion.h1>

            <motion.p
              className="mt-2 text-slate-400"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: 0.15 }}
            >
              Login to Intelligent Ticket Management System
            </motion.p>
          </motion.div>

          {/* Post password-change notice */}
          <AnimatePresence>
            {(location.state as { passwordChanged?: boolean } | null)
              ?.passwordChanged && (
              <motion.div
                key="password-changed"
                className="mb-5 rounded-lg border border-emerald-600 bg-emerald-900/30 p-3 text-sm text-emerald-300"
                initial={{ opacity: 0, y: -10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.98 }}
                transition={{ duration: 0.2 }}
              >
                Your password was changed successfully. Please sign in again
                with your new password.
              </motion.div>
            )}
          </AnimatePresence>

          {/* Email */}
          <motion.div className="relative mb-5" variants={itemVariants}>
            <motion.div
              className="absolute left-4 top-4 text-slate-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <Mail size={18} />
            </motion.div>

            <motion.input
              type="email"
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-4 text-white outline-none transition-colors focus:border-blue-500"
              whileFocus={reducedMotion ? {} : { scale: 1.01 }}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            />
          </motion.div>

          {/* Password */}
          <motion.div className="relative mb-4" variants={itemVariants}>
            <motion.div
              className="absolute left-4 top-4 text-slate-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
            >
              <Lock size={18} />
            </motion.div>

            <motion.input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border border-slate-700 bg-slate-800 py-3 pl-11 pr-12 text-white outline-none transition-colors focus:border-blue-500"
              whileFocus={reducedMotion ? {} : { scale: 1.01 }}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.15 }}
            />

            <motion.button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-3 text-slate-400 transition-colors hover:text-white"
              whileHover={reducedMotion ? {} : { scale: 1.1 }}
              whileTap={reducedMotion ? {} : { scale: 0.9 }}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </motion.button>
          </motion.div>

          {/* Remember + Forgot */}
          <motion.div className="mb-5 flex items-center justify-between" variants={itemVariants}>
            <motion.label
              className="flex items-center gap-2 text-sm text-slate-400"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.1 }}
            >
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="rounded border-slate-600 bg-slate-800 text-blue-600 focus:ring-blue-500"
              />
              Remember Me
            </motion.label>

            <motion.button
              type="button"
              onClick={() => alert("Password reset is not implemented in this demo.")}
              className="text-sm text-blue-400 hover:text-blue-300"
              whileHover={reducedMotion ? {} : { scale: 1.02 }}
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.2, delay: 0.15 }}
            >
              Forgot Password?
            </motion.button>
          </motion.div>

          {/* Error */}
          <AnimatePresence>
            {error && (
              <motion.div
                key="error"
                className="mb-5 rounded-lg border border-red-600 bg-red-900/30 p-3 text-sm text-red-300"
                initial={{ opacity: 0, y: -10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.98 }}
                transition={{ duration: 0.2 }}
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Login Button */}
          <motion.button
            type="submit"
            disabled={loading}
            className="w-full rounded-lg bg-gradient-to-r from-cyan-500 to-blue-600 py-3 font-semibold text-white shadow-lg shadow-cyan-500/20 transition-shadow duration-300 hover:shadow-cyan-400/40 disabled:bg-slate-700 disabled:bg-none disabled:shadow-none disabled:cursor-not-allowed"
            whileHover={reducedMotion || loading ? {} : { scale: 1.02 }}
            whileTap={reducedMotion || loading ? {} : { scale: 0.98 }}
            variants={itemVariants}
          >
            {loading ? "Logging in..." : "Login"}
          </motion.button>

          {/* Register */}
          <motion.p className="mt-6 text-center text-slate-400" variants={itemVariants}>
            Don't have an account?{" "}
            <Link to="/register" className="ml-2 font-semibold text-blue-400 hover:text-blue-300">
              Register
            </Link>
          </motion.p>
        </motion.form>
      </motion.div>
    </motion.div>
  );
}