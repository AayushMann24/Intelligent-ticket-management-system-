import { useNavigate } from "react-router-dom";

export default function DashboardHeader() {
  const navigate = useNavigate();

  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="mb-8 flex items-center justify-between">
      <div>
        <h1 className="text-4xl font-bold text-slate-900 transition-colors duration-300 dark:text-white">
          Welcome back, Aayush 👋
        </h1>

        <p className="mt-2 text-slate-500 transition-colors duration-300 dark:text-slate-400">
          {today}
        </p>
      </div>

      <button
        onClick={() => navigate("/tickets?create=true")}
        className="
          rounded-xl
          bg-blue-600
          px-6
          py-3
          font-semibold
          text-white
          transition-all
          duration-300
          hover:-translate-y-0.5
          hover:bg-blue-700
          hover:shadow-lg
        "
      >
        + Create Ticket
      </button>
    </div>
  );
}