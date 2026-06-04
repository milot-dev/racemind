"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
} from "recharts";
import { getRiderStats, getRiderTrends } from "@/lib/api";

type RiderStats = {
  rider: string;
  team_names: string[];
  total_entries: number;
  wins: number;
  podiums: number;
  top_10s: number;
  dnfs: number;
  average_finish: number | null;
  average_grid: number | null;
  total_points: number;
  best_finish: number | null;
  worst_finish: number | null;
};

type RiderTrend = {
  year: number;
  entries: number;
  wins: number;
  podiums: number;
  top_10s: number;
  dnfs: number;
  total_points: number;
  average_finish: number | null;
  average_grid: number | null;
};

type RecentResult = {
  year: number;
  event_name: string;
  session_type: string;
  team: string;
  grid_position: number | null;
  finish_position: number | null;
  points: number;
  status: string;
};

type RiderTrendsResponse = {
  rider: string;
  team_history: {
    year: number;
    team: string;
  }[];
  yearly_trends: RiderTrend[];
  recent_results: RecentResult[];
};

export default function RiderProfilePage() {
  const params = useParams();
  const riderName = decodeURIComponent(String(params.name));

  const [stats, setStats] = useState<RiderStats | null>(null);
  const [trends, setTrends] = useState<RiderTrendsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const teams = useMemo(() => {
    if (!trends?.team_history) return [];

    return Array.from(
      new Set(trends.team_history.map((item) => item.team).filter(Boolean))
    );
  }, [trends]);

    useEffect(() => {
    async function loadRiderProfile() {
        try {
        setLoading(true);

        const [statsData, trendsData] = await Promise.all([
            getRiderStats<RiderStats>(riderName),
            getRiderTrends<RiderTrendsResponse>(riderName),
        ]);

        setStats(statsData);
        setTrends(trendsData);
        } catch (err) {
        setError(
            err instanceof Error
            ? err.message
            : "Failed to load rider profile."
        );
        } finally {
        setLoading(false);
        }
    }

    loadRiderProfile();
    }, [riderName]);

  if (loading) {
    return (
      <main className="min-h-screen bg-black px-6 py-10 text-white">
        <p className="text-zinc-400">Loading rider profile...</p>
      </main>
    );
  }

  if (error || !stats || !trends) {
    return (
      <main className="min-h-screen bg-black px-6 py-10 text-white">
        <p className="text-red-400">{error || "Rider profile not found."}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-black px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <p className="text-sm uppercase tracking-[0.3em] text-red-400">
          Rider Profile
        </p>

        <h1 className="mt-3 text-4xl font-black">
          {stats.rider}
        </h1>

        <p className="mt-3 max-w-3xl text-zinc-400">
          Historical MotoGP performance profile based on cleaned RaceMind AI
          race result data.
        </p>

        <div className="mt-8 grid gap-4 md:grid-cols-4">
          <Stat label="Total Points" value={stats.total_points} />
          <Stat label="Wins" value={stats.wins} />
          <Stat label="Podiums" value={stats.podiums} />
          <Stat label="DNFs" value={stats.dnfs} />
        </div>

        <section className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
          <h2 className="text-2xl font-bold">Team History</h2>

          <div className="mt-4 flex flex-wrap gap-2">
            {teams.map((team) => (
              <span
                key={team}
                className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-sm text-red-100"
              >
                {team}
              </span>
            ))}
          </div>
        </section>

        <section className="mt-8 grid min-w-0 gap-6 lg:grid-cols-2">          <div className="rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
            <h2 className="text-xl font-bold">Points by Season</h2>

            <div className="mt-6 h-[320px] min-h-[320px] w-full min-w-0 overflow-hidden">
                <ResponsiveContainer width="100%" height={320}>
                <BarChart data={trends.yearly_trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis 
                    dataKey="year" 
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
                  <Bar dataKey="total_points" fill="#dc2626" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
            <h2 className="text-xl font-bold">Average Finish Trend</h2>

            <div className="mt-6 h-[320px] min-h-[320px] w-full min-w-0 overflow-hidden">
                <ResponsiveContainer width="100%" height={320}>
                <LineChart data={trends.yearly_trends}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis 
                    dataKey="year" 
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

                  <Line
                    type="monotone"
                    dataKey="average_finish"
                    strokeWidth={2}
                    stroke="#dc2626" 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
          <h2 className="text-2xl font-bold">Recent Results</h2>

          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-zinc-400">
                <tr>
                  <th className="p-3">Year</th>
                  <th className="p-3">Event</th>
                  <th className="p-3">Session</th>
                  <th className="p-3">Grid</th>
                  <th className="p-3">Finish</th>
                  <th className="p-3">Points</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {trends.recent_results.map((row, index) => (
                  <tr key={index} className="border-t border-zinc-800">
                    <td className="p-3">{row.year}</td>
                    <td className="p-3">{row.event_name}</td>
                    <td className="p-3">{row.session_type}</td>
                    <td className="p-3">{row.grid_position ?? "-"}</td>
                    <td className="p-3">{row.finish_position ?? "-"}</td>
                    <td className="p-3">{row.points}</td>
                    <td className="p-3">{row.status || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string | number | null }) {
  return (
    <div className="rounded-2xl border border-red-500/20 bg-zinc-950 p-5">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="mt-2 text-3xl font-black text-white">
        {value ?? "-"}
      </p>
    </div>
  );
}