import { useNavigate } from "react-router-dom";
import { motion, type Variants } from "framer-motion";
import {
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  Bot,
  Brain,
  CheckCircle2,
  Gauge,
  ShieldCheck,
  Sparkles,
  Users,
  Workflow,
  Zap,
} from "lucide-react";

import AnimatedBackground from "../components/common/AnimatedBackground";
import Reveal from "../components/common/Reveal";
import { useReducedMotion } from "../hooks/useReducedMotion";

const EASE: [number, number, number, number] = [0.22, 1, 0.36, 1];

const container: Variants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.12, delayChildren: 0.1 },
  },
};

const item: Variants = {
  hidden: { opacity: 0, y: 26 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.65, ease: EASE },
  },
};

const features = [
  {
    icon: Brain,
    title: "AI Classification",
    description:
      "Incoming tickets are categorised and summarised automatically, so nothing is triaged by hand.",
    accent: "from-cyan-400/25 to-cyan-400/0",
  },
  {
    icon: Zap,
    title: "Priority Detection",
    description:
      "Urgency is predicted with a reasoning trail, keeping critical issues at the top of the queue.",
    accent: "from-amber-400/25 to-amber-400/0",
  },
  {
    icon: Users,
    title: "Smart Assignment",
    description:
      "Tickets are routed to the most suitable technician with an explanation for every decision.",
    accent: "from-violet-400/25 to-violet-400/0",
  },
  {
    icon: Gauge,
    title: "SLA & Escalation",
    description:
      "Response and resolution targets are tracked continuously, with automatic escalation on breach.",
    accent: "from-emerald-400/25 to-emerald-400/0",
  },
  {
    icon: BookOpen,
    title: "Knowledge Base",
    description:
      "A vector-search knowledge base with citations, keeping answers grounded and auditable.",
    accent: "from-blue-400/25 to-blue-400/0",
  },
  {
    icon: Bot,
    title: "Grounded Assistant",
    description:
      "An AI assistant that answers from real knowledge and ticket context, never from thin air.",
    accent: "from-fuchsia-400/25 to-fuchsia-400/0",
  },
];

const steps = [
  {
    number: "01",
    icon: Workflow,
    title: "Capture",
    description:
      "Employees raise tickets through a guided form while AI enriches each one instantly.",
  },
  {
    number: "02",
    icon: Sparkles,
    title: "Triage",
    description:
      "Classification, prioritisation and assignment happen in one automated pass.",
  },
  {
    number: "03",
    icon: BarChart3,
    title: "Resolve & Measure",
    description:
      "Technicians work the queue while SLAs, analytics and reports stay live.",
  },
];

const capabilities = [
  { icon: ShieldCheck, label: "Role-based access" },
  { icon: Bell, label: "Real-time notifications" },
  { icon: CheckCircle2, label: "Auditable history" },
  { icon: BarChart3, label: "Analytics & reporting" },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const reducedMotion = useReducedMotion();

  const hover = (scale: number) => (reducedMotion ? {} : { scale });
  const tap = reducedMotion ? {} : { scale: 0.97 };

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-[#05070f] text-white">
      <AnimatedBackground variant="public" />

      {/* -------------------------------------------------- Nav */}
      <header className="fixed inset-x-0 top-0 z-50 px-4 pt-4 sm:px-6">
        <motion.nav
          initial={reducedMotion ? undefined : { opacity: 0, y: -18 }}
          animate={reducedMotion ? undefined : { opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="itms-glass-strong mx-auto flex max-w-6xl items-center justify-between rounded-2xl px-4 py-3 shadow-2xl shadow-black/40"
        >
          <button
            type="button"
            onClick={() => navigate("/")}
            className="flex items-center gap-2 rounded-lg text-lg font-bold tracking-tight transition-colors hover:text-cyan-300"
          >
            <span aria-hidden="true">🤖</span>
            <span>ITMS</span>
          </button>

          <div className="flex items-center gap-2 sm:gap-3">
            <motion.button
              type="button"
              onClick={() => navigate("/login")}
              whileHover={hover(1.03)}
              whileTap={tap}
              className="rounded-xl px-4 py-2 text-sm font-medium text-slate-200 transition-colors hover:bg-white/5 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
            >
              Login
            </motion.button>

            <motion.button
              type="button"
              onClick={() => navigate("/register")}
              whileHover={hover(1.03)}
              whileTap={tap}
              className="rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-cyan-500/20 transition-shadow hover:shadow-cyan-500/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
            >
              Get Started
            </motion.button>
          </div>
        </motion.nav>
      </header>

      {/* -------------------------------------------------- Hero */}
      <section className="relative flex min-h-screen items-center px-6 pt-32 pb-20">
        <div className="mx-auto grid w-full max-w-6xl items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
          <motion.div variants={container} initial="hidden" animate="show">
            <motion.span
              variants={item}
              className="itms-glass inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium tracking-wide text-cyan-200 sm:text-sm"
            >
              <Sparkles size={15} className="text-cyan-300" />
              AI-powered ITSM platform
            </motion.span>

            <motion.h1
              variants={item}
              className="mt-6 text-4xl font-extrabold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl"
            >
              Intelligent Ticket
              <br />
              <span className="itms-text-gradient">Management System</span>
            </motion.h1>

            <motion.p
              variants={item}
              className="mt-6 max-w-xl text-base leading-relaxed text-slate-300/90 sm:text-lg"
            >
              Classify, prioritise and assign support tickets automatically.
              Track SLAs, surface analytics, and ground every answer in a
              searchable knowledge base — all from one platform.
            </motion.p>

            <motion.div variants={item} className="mt-9 flex flex-wrap items-center gap-4">
              <motion.button
                type="button"
                onClick={() => navigate("/login")}
                whileHover={hover(1.04)}
                whileTap={tap}
                className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3.5 text-base font-semibold shadow-xl shadow-cyan-500/25 transition-shadow hover:shadow-cyan-400/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
              >
                Login to Dashboard
                <ArrowRight
                  size={18}
                  className="transition-transform duration-300 group-hover:translate-x-1"
                />
              </motion.button>

              <motion.button
                type="button"
                onClick={() => navigate("/register")}
                whileHover={hover(1.04)}
                whileTap={tap}
                className="itms-glass inline-flex items-center gap-2 rounded-xl px-7 py-3.5 text-base font-semibold text-slate-100 transition-colors hover:border-cyan-400/50 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
              >
                Create an Account
              </motion.button>
            </motion.div>

            <motion.div
              variants={item}
              className="mt-10 flex flex-wrap items-center gap-x-6 gap-y-3 text-sm text-slate-400"
            >
              {capabilities.map(({ icon: Icon, label }) => (
                <span key={label} className="inline-flex items-center gap-2">
                  <Icon size={16} className="text-cyan-300" />
                  {label}
                </span>
              ))}
            </motion.div>
          </motion.div>

          {/* Hero preview */}
          <motion.div
            initial={reducedMotion ? undefined : { opacity: 0, y: 40, scale: 0.96 }}
            animate={reducedMotion ? undefined : { opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="relative"
          >
            <motion.div
              animate={reducedMotion ? undefined : { y: [0, -14, 0] }}
              transition={{ duration: 7, repeat: Infinity, ease: "easeInOut" }}
              className="itms-glass-strong relative rounded-3xl p-5 shadow-2xl shadow-black/50"
            >
              {/* window chrome */}
              <div className="mb-4 flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-red-400/80" />
                <span className="h-3 w-3 rounded-full bg-amber-400/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-400/80" />
                <span className="ml-3 text-xs text-slate-400">
                  ITMS · Service Desk
                </span>
              </div>

              {/* stat row */}
              <div className="grid grid-cols-3 gap-3">
                {["Open", "Assigned", "Resolved"].map((label, index) => (
                  <div
                    key={label}
                    className="rounded-2xl border border-white/5 bg-white/5 p-3"
                  >
                    <p className="text-[11px] uppercase tracking-wide text-slate-400">
                      {label}
                    </p>
                    <div
                      className={`itms-shimmer mt-2 h-5 w-10 rounded-md ${
                        index === 1 ? "opacity-70" : ""
                      }`}
                    />
                  </div>
                ))}
              </div>

              {/* chart skeleton */}
              <div className="mt-4 rounded-2xl border border-white/5 bg-white/5 p-4">
                <div className="flex items-end gap-2" aria-hidden="true">
                  {[38, 62, 46, 78, 54, 88, 66, 92].map((height, index) => (
                    <div
                      key={index}
                      className="itms-shimmer w-full rounded-md"
                      style={{ height: `${height}px` }}
                    />
                  ))}
                </div>
              </div>

              {/* AI assistant bubble */}
              <div className="mt-4 flex items-start gap-3 rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-4">
                <span className="flex h-9 w-9 flex-none items-center justify-center rounded-full bg-cyan-500/20 text-cyan-200">
                  <Bot size={18} />
                </span>
                <div className="w-full">
                  <p className="text-sm font-medium text-cyan-100">
                    Assistant grounded in the knowledge base
                  </p>
                  <div className="mt-3 space-y-2">
                    <div className="itms-shimmer h-3 w-full rounded" />
                    <div className="itms-shimmer h-3 w-4/5 rounded" />
                  </div>
                </div>
              </div>
            </motion.div>

            {/* floating accent */}
            <div className="pointer-events-none absolute -right-6 -top-6 hidden h-24 w-24 rounded-3xl bg-gradient-to-br from-fuchsia-500/30 to-transparent blur-xl sm:block" />
          </motion.div>
        </div>

        {/* scroll hint */}
        {!reducedMotion && (
          <div className="pointer-events-none absolute bottom-8 left-1/2 hidden -translate-x-1/2 flex-col items-center gap-2 text-slate-500 md:flex">
            <span className="text-xs uppercase tracking-[0.3em]">Scroll</span>
            <span className="itms-scroll-hint h-8 w-px bg-gradient-to-b from-cyan-400/70 to-transparent" />
          </div>
        )}
      </section>

      {/* -------------------------------------------------- Features */}
      <section className="relative px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything a modern service desk needs
            </h2>
            <p className="mt-4 text-slate-400">
              A cohesive platform where automation, accountability and insight
              work together.
            </p>
          </Reveal>

          <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map(({ icon: Icon, title, description, accent }, index) => (
              <Reveal key={title} delay={index * 0.06}>
                <article className="itms-glass itms-card-glow group h-full rounded-2xl p-6">
                  <span
                    className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${accent} text-cyan-200 ring-1 ring-white/10`}
                  >
                    <Icon size={22} />
                  </span>
                  <h3 className="mt-5 text-lg font-semibold text-white">
                    {title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">
                    {description}
                  </p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* -------------------------------------------------- Workflow */}
      <section className="relative px-6 py-24">
        <div className="mx-auto max-w-6xl">
          <Reveal className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              From ticket to resolution
            </h2>
            <p className="mt-4 text-slate-400">
              A flow that stays fast under pressure and transparent at every
              step.
            </p>
          </Reveal>

          <div className="mt-14 grid gap-6 md:grid-cols-3">
            {steps.map(({ number, icon: Icon, title, description }, index) => (
              <Reveal key={title} delay={index * 0.1} direction="up">
                <article className="itms-glass relative h-full overflow-hidden rounded-2xl p-7">
                  <span className="absolute right-5 top-4 text-5xl font-black text-white/5">
                    {number}
                  </span>
                  <span className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-white/5 text-cyan-300 ring-1 ring-white/10">
                    <Icon size={20} />
                  </span>
                  <h3 className="mt-5 text-lg font-semibold text-white">
                    {title}
                  </h3>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">
                    {description}
                  </p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* -------------------------------------------------- CTA */}
      <section className="relative px-6 pb-24 pt-8">
        <Reveal className="mx-auto max-w-5xl">
          <div className="itms-glass-strong relative overflow-hidden rounded-3xl px-8 py-14 text-center shadow-2xl shadow-black/40">
            <div className="pointer-events-none absolute -left-16 -top-16 h-56 w-56 rounded-full bg-cyan-500/20 blur-3xl" />
            <div className="pointer-events-none absolute -bottom-20 -right-10 h-56 w-56 rounded-full bg-violet-500/20 blur-3xl" />

            <h2 className="relative text-3xl font-bold tracking-tight sm:text-4xl">
              Ready to bring order to your queue?
            </h2>
            <p className="relative mx-auto mt-4 max-w-xl text-slate-300">
              Sign in to explore the dashboard, or create an account to start
              managing tickets with AI assistance.
            </p>

            <div className="relative mt-8 flex flex-wrap items-center justify-center gap-4">
              <motion.button
                type="button"
                onClick={() => navigate("/login")}
                whileHover={hover(1.04)}
                whileTap={tap}
                className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-7 py-3.5 text-base font-semibold shadow-xl shadow-cyan-500/25 transition-shadow hover:shadow-cyan-400/50 focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-300"
              >
                Login
                <ArrowRight
                  size={18}
                  className="transition-transform duration-300 group-hover:translate-x-1"
                />
              </motion.button>

              <motion.button
                type="button"
                onClick={() => navigate("/register")}
                whileHover={hover(1.04)}
                whileTap={tap}
                className="itms-glass rounded-xl px-7 py-3.5 text-base font-semibold text-slate-100 transition-colors hover:border-cyan-400/50 hover:text-white focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400"
              >
                Register
              </motion.button>
            </div>
          </div>
        </Reveal>
      </section>

      {/* -------------------------------------------------- Footer */}
      <footer className="relative border-t border-white/5 px-6 py-10">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 text-sm text-slate-500 sm:flex-row">
          <span className="inline-flex items-center gap-2">
            <span aria-hidden="true">🤖</span>
            Intelligent Ticket Management System
          </span>
          <span>Built for IT support teams.</span>
        </div>
      </footer>
    </div>
  );
}
