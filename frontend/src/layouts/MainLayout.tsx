import type { ReactNode } from "react";

import Sidebar from "../components/layout/Sidebar";
import Navbar from "../components/layout/Navbar";

interface MainLayoutProps {
  children: ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="flex min-h-screen bg-slate-950">

      <Sidebar />

      <div className="flex flex-1 flex-col">

        <Navbar />

        <main className="flex-1 p-8 overflow-auto">
          {children}
        </main>

      </div>

    </div>
  );
}