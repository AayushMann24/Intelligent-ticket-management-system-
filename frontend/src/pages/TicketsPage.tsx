import MainLayout from "../layouts/MainLayout";

import useTickets from "../hooks/useTickets";

import TicketTable from "../components/tickets/TicketTable";
import TicketToolbar from "../components/tickets/TicketToolbar";

export default function TicketsPage() {
  const {
    tickets,
    loading,

    search,
    setSearch,

    status,
    setStatus,

    priority,
    setPriority,
  } = useTickets();

  if (loading) {
    return (
      <MainLayout>
        <div className="flex h-96 items-center justify-center">
          <h2 className="text-xl text-white">
            Loading Tickets...
          </h2>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <h1 className="mb-8 text-3xl font-bold text-white">
        Tickets
      </h1>

      <TicketToolbar
        search={search}
        setSearch={setSearch}
        status={status}
        setStatus={setStatus}
        priority={priority}
        setPriority={setPriority}
      />

      <TicketTable tickets={tickets} />
    </MainLayout>
  );
}