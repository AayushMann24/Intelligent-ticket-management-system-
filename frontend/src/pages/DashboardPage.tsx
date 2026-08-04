import MainLayout from "../layouts/MainLayout";

export default function DashboardPage() {
  return (
    <MainLayout>

      <h1 className="text-4xl font-bold text-white">
        Dashboard
      </h1>

      <p className="mt-2 text-zinc-400">
        Welcome back 👋
      </p>

    </MainLayout>
  );
}