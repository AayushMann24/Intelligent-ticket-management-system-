import { useEffect, useState } from "react";

import MainLayout from "../layouts/MainLayout";

import {
    getDashboardSummary,
    getRecentActivity,
    getRecentTickets,
} from "../services/dashboardService";

import type {
    DashboardSummary,
    RecentTicket,
    Activity,
} from "../services/dashboardService";

export default function AnalyticsPage() {

    const [summary, setSummary] =
        useState<DashboardSummary | null>(null);

    const [tickets, setTickets] =
        useState<RecentTicket[]>([]);

    const [activity, setActivity] =
        useState<Activity[]>([]);

    const [loading, setLoading] =
        useState(true);

    useEffect(() => {

        async function loadDashboard() {

            try {

                const [
                    summaryData,
                    recentTickets,
                    activityData,
                ] = await Promise.all([
                    getDashboardSummary(),
                    getRecentTickets(),
                    getRecentActivity(),
                ]);

                setSummary(summaryData);
                setTickets(recentTickets);
                setActivity(activityData);

            } catch (error) {

                console.error(error);

            } finally {

                setLoading(false);

            }

        }

        loadDashboard();

    }, []);

    if (loading) {
        return (
            <MainLayout>
                <h2 className="text-white text-xl">
                    Loading Analytics...
                </h2>
            </MainLayout>
        );
    }

    return (
        <MainLayout>

            <h1 className="text-3xl font-bold text-white mb-8">
                Analytics Dashboard
            </h1>

            {/* KPI Cards */}

            <div className="grid grid-cols-4 gap-6">

                <Card title="Total Tickets" value={summary?.total_tickets} />

                <Card title="Open" value={summary?.open_tickets} />

                <Card title="Assigned" value={summary?.assigned_tickets} />

                <Card title="Resolved" value={summary?.resolved_tickets} />

            </div>

            <div className="grid grid-cols-3 gap-6 mt-6">

                <Card title="High Priority" value={summary?.high_priority} />

                <Card title="Medium Priority" value={summary?.medium_priority} />

                <Card title="Low Priority" value={summary?.low_priority} />

            </div>

            {/* Recent Tickets */}

            <div className="bg-slate-900 rounded-xl p-6 mt-8">

                <h2 className="text-white text-xl font-semibold mb-4">
                    Recent Tickets
                </h2>

                <table className="w-full text-white">

                    <thead>

                        <tr className="border-b border-slate-700">

                            <th className="text-left py-2">Title</th>

                            <th>Status</th>

                            <th>Priority</th>

                            <th>Assigned To</th>

                        </tr>

                    </thead>

                    <tbody>

                        {tickets.map(ticket => (

                            <tr
                                key={ticket.id}
                                className="border-b border-slate-800"
                            >

                                <td className="py-3">
                                    {ticket.title}
                                </td>

                                <td>
                                    {ticket.status}
                                </td>

                                <td>
                                    {ticket.priority}
                                </td>

                                <td>
                                    {ticket.assigned_to}
                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

            {/* Activity */}

            <div className="bg-slate-900 rounded-xl p-6 mt-8">

                <h2 className="text-white text-xl font-semibold mb-4">
                    Recent Activity
                </h2>

                {activity.map((item, index) => (

                    <div
                        key={index}
                        className="border-b border-slate-700 py-3"
                    >

                        <p className="text-white">
                            {item.message}
                        </p>

                        <p className="text-slate-400 text-sm">
                            {item.time}
                        </p>

                    </div>

                ))}

            </div>

        </MainLayout>
    );
}

interface CardProps {

    title: string;

    value: number | undefined;

}

function Card({
    title,
    value,
}: CardProps) {

    return (

        <div className="bg-slate-900 rounded-xl p-6">

            <p className="text-slate-400">
                {title}
            </p>

            <h2 className="text-3xl font-bold text-white mt-3">
                {value ?? 0}
            </h2>

        </div>

    );

}