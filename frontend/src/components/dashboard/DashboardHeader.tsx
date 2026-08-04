export default function DashboardHeader() {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="mb-8 flex items-center justify-between">
      <div>
        <h1 className="text-4xl font-bold text-white">
          Welcome back, Aayush 👋
        </h1>

        <p className="mt-2 text-zinc-400">
          {today}
        </p>
      </div>

      <button className="rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700">
        + Create Ticket
      </button>
    </div>
  );
}