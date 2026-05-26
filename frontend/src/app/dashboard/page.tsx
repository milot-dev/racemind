"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import StatCard from "@/components/StatCard";
import { apiGet } from "@/lib/api";

type DashboardData = {
  total_riders: number;
  total_events: number;
  total_teams: number;
  years_covered: number[];
  total_rows: number;
  session_types: string[];
  top_points_riders: { rider: string; points: number }[];
  top_winners: { rider: string; wins: number }[];
  podium_leaders: { rider: string; podiums: number }[];
  average_finish_leaders: { rider: string; average_finish: number }[];
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet<DashboardData>("/dashboard")
      .then(setData)
      .catch((err) => setError(err.message || "Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <main className="px-6 py-16">
        <p className="text-zinc-300">Loading MotoGP dashboard...</p>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="px-6 py-16">
        <p className="text-red-400">Error: {error}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-6 py-12">
      <section className="mx-auto max-w-7xl">
        <div className="mb-10">
          <p className="text-sm uppercase tracking-[0.3em] text-red-400">
            MotoGP Analytics
          </p>
          <h1 className="mt-3 text-4xl font-black text-white md:text-5xl">
            Race Dashboard
          </h1>
          <p className="mt-4 max-w-2xl text-zinc-400">
            Explore cleaned MotoGP race and sprint result data from{" "}
            {data.years_covered.join(", ")}.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Total Riders" value={data.total_riders} />
          <StatCard label="Total Events" value={data.total_events} />
          <StatCard label="Total Teams" value={data.total_teams} />
          <StatCard label="Rows Analyzed" value={data.total_rows} />
        </div>

        <section className="mt-10 min-w-0 rounded-2xl border border-red-500/20 bg-gradient-to-br from-zinc-950 via-black to-red-950/30 p-6">
        <h2 className="text-2xl font-bold text-white">Top Points Riders</h2>

        <div className="mt-6 h-[360px] min-h-[360px] w-full min-w-0">
            <ResponsiveContainer width="100%" height={360}>
            <BarChart data={data.top_points_riders}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />

                <XAxis
                dataKey="rider"
                tick={{ fill: "#d4d4d8", fontSize: 12 }}
                axisLine={{ stroke: "#3f3f46" }}
                tickLine={{ stroke: "#3f3f46" }}
                />

                <YAxis
                tick={{ fill: "#d4d4d8", fontSize: 12 }}
                axisLine={{ stroke: "#3f3f46" }}
                tickLine={{ stroke: "#3f3f46" }}
                />

                <Tooltip
                contentStyle={{
                    backgroundColor: "#09090b",
                    border: "1px solid #27272a",
                    borderRadius: "12px",
                    color: "#ffffff",
                }}
                labelStyle={{
                    color: "#ffffff",
                }}
                cursor={{
                    fill: "rgba(220, 38, 38, 0.08)",
                }}
                />

                <Bar dataKey="points" fill="#dc2626" radius={[8, 8, 0, 0]} />
            </BarChart>
            </ResponsiveContainer>
        </div>
        </section>

        <section className="mt-10 grid gap-6 lg:grid-cols-3">
          <LeaderboardTable
            title="Top Winners"
            data={data.top_winners}
            valueKey="wins"
            valueLabel="Wins"
          />

          <LeaderboardTable
            title="Podium Leaders"
            data={data.podium_leaders}
            valueKey="podiums"
            valueLabel="Podiums"
          />

          <LeaderboardTable
            title="Best Average Finish"
            data={data.average_finish_leaders}
            valueKey="average_finish"
            valueLabel="Avg Finish"
          />
        </section>
      </section>
    </main>
  );
}

function LeaderboardTable({
  title,
  data,
  valueKey,
  valueLabel,
}: {
  title: string;
  data: Record<string, string | number>[];
  valueKey: string;
  valueLabel: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
      <h3 className="text-xl font-bold text-white">{title}</h3>

      <div className="mt-5 space-y-3">
        {data.map((row, index) => (
          <div
            key={`${row.rider}-${index}`}
            className="flex items-center justify-between rounded-xl bg-black/30 px-4 py-3"
          >
            <div>
              <p className="font-semibold text-white">{row.rider}</p>
              <p className="text-xs text-zinc-500">Rank #{index + 1}</p>
            </div>

            <div className="text-right">
              <p className="font-bold text-red-400">{row[valueKey]}</p>
              <p className="text-xs text-zinc-500">{valueLabel}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}