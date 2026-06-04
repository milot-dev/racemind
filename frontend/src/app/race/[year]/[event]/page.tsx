"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type RaceResult = {
  year: number;
  event_name: string;
  session_type: string;
  circuit: string;
  rider: string;
  team: string;
  grid_position: number | null;
  finish_position: number | null;
  points: number;
  status: string;
};

type RaceDetail = {
  year: number;
  event_name: string;
  circuit: string;
  results: RaceResult[];
  podium: {
    finish_position: number;
    rider: string;
    team: string;
    points: number;
    session_type: string;
  }[];
  session_summary: {
    session_type: string;
    entries: number;
    points_awarded: number;
    winner: string;
  }[];
  team_points: {
    team: string;
    total_points: number;
  }[];
  ai_summary: string;
};

export default function RaceDetailPage() {
  const params = useParams();

  const year = String(params.year);
  const event = decodeURIComponent(String(params.event));

  const [data, setData] = useState<RaceDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadRace() {
      try {
        setLoading(true);

        const response = await fetch(
          `${API_BASE_URL}/race/${year}/${encodeURIComponent(event)}`
        );

        if (!response.ok) {
          throw new Error("Failed to load race detail");
        }

        const result = await response.json();

        if (result.error) {
          throw new Error(result.error);
        }

        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Something went wrong");
      } finally {
        setLoading(false);
      }
    }

    loadRace();
  }, [year, event]);

  if (loading) {
    return (
      <main className="min-h-screen bg-black px-6 py-10 text-white">
        <p className="text-zinc-400">Loading race detail...</p>
      </main>
    );
  }

  if (error || !data) {
    return (
      <main className="min-h-screen bg-black px-6 py-10 text-white">
        <p className="text-red-400">{error || "Race not found."}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-black px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <p className="text-sm uppercase tracking-[0.3em] text-red-400">
          Race Detail
        </p>

        <h1 className="mt-3 text-4xl font-black">
          {data.year} {data.event_name}
        </h1>

        <p className="mt-3 text-zinc-400">
          Circuit: {data.circuit || "Unknown"}
        </p>

        <section className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
          <h2 className="text-2xl font-bold">AI Race Summary</h2>
          <p className="mt-4 leading-7 text-zinc-300">
            {data.ai_summary}
          </p>
        </section>

        <section className="mt-8 grid min-w-0 gap-6 lg:grid-cols-2">          <div className="rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
            <h2 className="text-xl font-bold">Team Points</h2>

            <div className="mt-6 h-[320px] min-h-[320px] w-full min-w-0 overflow-hidden">
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={data.team_points}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                  <XAxis
                    dataKey="team"
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

            <div className="min-w-0 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">            
            <h2 className="text-xl font-bold">Session Summary</h2>

            <div className="mt-6 space-y-3">
              {data.session_summary.map((item) => (
                <div
                  key={item.session_type}
                  className="rounded-xl border border-zinc-800 bg-black/40 p-4"
                >
                  <p className="font-bold">{item.session_type}</p>
                  <p className="mt-2 text-sm text-zinc-400">
                    Entries: {item.entries}
                  </p>
                  <p className="text-sm text-zinc-400">
                    Winner: {item.winner || "-"}
                  </p>
                  <p className="text-sm text-zinc-400">
                    Points awarded: {item.points_awarded}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
          <h2 className="text-2xl font-bold">Podium</h2>

          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {data.podium.map((item, index) => (
            <div
                key={`${item.session_type}-${item.finish_position}-${item.rider}-${index}`}
                className="rounded-xl border border-red-500/20 bg-black/40 p-5"
              >
                <p className="text-sm text-red-300">
                  P{item.finish_position} · {item.session_type}
                </p>
                <p className="mt-2 text-xl font-bold">{item.rider}</p>
                <p className="mt-1 text-sm text-zinc-400">{item.team}</p>
                <p className="mt-2 text-sm text-zinc-300">
                  {item.points} points
                </p>
              </div>
            ))}
          </div>
        </section>

        <section className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-6">
          <h2 className="text-2xl font-bold">Full Results</h2>

          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-zinc-400">
                <tr>
                  <th className="p-3">Session</th>
                  <th className="p-3">Rider</th>
                  <th className="p-3">Team</th>
                  <th className="p-3">Grid</th>
                  <th className="p-3">Finish</th>
                  <th className="p-3">Points</th>
                  <th className="p-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.results.map((row, index) => (
                  <tr key={index} className="border-t border-zinc-800">
                    <td className="p-3">{row.session_type}</td>
                    <td className="p-3">{row.rider}</td>
                    <td className="p-3">{row.team}</td>
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