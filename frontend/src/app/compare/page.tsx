"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import RiderSelector from "@/components/RiderSelector";
import RiderStatsCard, { RiderStats } from "@/components/RiderStatsCard";
import { apiGet } from "@/lib/api";

type RidersResponse = {
  riders: string[];
};

type ComparisonResponse = {
  rider_a: RiderStats;
  rider_b: RiderStats;
  insights: {
    higher_points: string;
    more_wins: string;
    more_podiums: string;
    better_average_finish: string;
    fewer_dnfs: string;
    more_consistent_rider: string;
  };
};

export default function ComparePage() {
  const [riders, setRiders] = useState<string[]>([]);
  const [riderA, setRiderA] = useState("");
  const [riderB, setRiderB] = useState("");

  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [loadingRiders, setLoadingRiders] = useState(true);
  const [loadingComparison, setLoadingComparison] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    apiGet<RidersResponse>("/riders")
      .then((data) => {
        setRiders(data.riders);
      })
      .catch((err) => {
        setError(err.message || "Failed to load riders.");
      })
      .finally(() => {
        setLoadingRiders(false);
      });
  }, []);

  useEffect(() => {
    if (!riderA || !riderB || riderA === riderB) {
      setComparison(null);
      return;
    }

    setLoadingComparison(true);
    setError("");

    const query = `/compare?rider_a=${encodeURIComponent(
      riderA
    )}&rider_b=${encodeURIComponent(riderB)}`;

    apiGet<ComparisonResponse>(query)
      .then(setComparison)
      .catch((err) => {
        setError(err.message || "Failed to compare riders.");
      })
      .finally(() => {
        setLoadingComparison(false);
      });
  }, [riderA, riderB]);

  const chartData = useMemo(() => {
    if (!comparison) return [];

    return [
      {
        metric: "Points",
        [comparison.rider_a.rider]: comparison.rider_a.total_points,
        [comparison.rider_b.rider]: comparison.rider_b.total_points,
      },
      {
        metric: "Wins",
        [comparison.rider_a.rider]: comparison.rider_a.wins,
        [comparison.rider_b.rider]: comparison.rider_b.wins,
      },
      {
        metric: "Podiums",
        [comparison.rider_a.rider]: comparison.rider_a.podiums,
        [comparison.rider_b.rider]: comparison.rider_b.podiums,
      },
      {
        metric: "Top 10s",
        [comparison.rider_a.rider]: comparison.rider_a.top_10s,
        [comparison.rider_b.rider]: comparison.rider_b.top_10s,
      },
      {
        metric: "DNFs",
        [comparison.rider_a.rider]: comparison.rider_a.dnfs,
        [comparison.rider_b.rider]: comparison.rider_b.dnfs,
      },
    ];
  }, [comparison]);

  return (
    <main className="min-h-screen px-6 py-12">
      <section className="mx-auto max-w-7xl">
        <div className="mb-10">
          <p className="text-sm uppercase tracking-[0.3em] text-red-400">
            Rider Analytics
          </p>
          <h1 className="mt-3 text-4xl font-black text-white md:text-5xl">
            Rider Comparison
          </h1>
          <p className="mt-4 max-w-2xl text-zinc-400">
            Compare two MotoGP riders using real cleaned race and sprint result
            data from the dataset.
          </p>
        </div>

        <section className="rounded-2xl border border-white/10 bg-white/4 p-6">
          {loadingRiders ? (
            <p className="text-zinc-300">Loading riders...</p>
          ) : (
            <div className="grid gap-5 md:grid-cols-2">
              <RiderSelector
                label="Rider A"
                riders={riders}
                value={riderA}
                onChange={setRiderA}
              />

              <RiderSelector
                label="Rider B"
                riders={riders}
                value={riderB}
                onChange={setRiderB}
              />
            </div>
          )}

          {riderA && riderB && riderA === riderB && (
            <p className="mt-4 text-sm text-yellow-400">
              Choose two different riders to compare.
            </p>
          )}
        </section>

        {error && (
          <div className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
            {error}
          </div>
        )}

        {loadingComparison && (
          <div className="mt-8 rounded-2xl border border-white/10 bg-white/4 p-6">
            <p className="text-zinc-300">Comparing riders...</p>
          </div>
        )}

        {!loadingComparison && comparison && (
          <>
            <section className="mt-8 grid gap-6 lg:grid-cols-2">
              <RiderStatsCard stats={comparison.rider_a} />
              <RiderStatsCard stats={comparison.rider_b} />
            </section>

            <section className="mt-8 min-w-0 rounded-2xl border border-red-500/20 bg-linear-to-br from-zinc-950 via-black to-red-950/30 p-6">
            <h2 className="text-2xl font-bold text-white">
                Metric Comparison
            </h2>

            <div className="mt-6 h-90 min-h-90 w-full min-w-0 overflow-hidden">
                <ResponsiveContainer width="100%" height={360}>
                <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />

                    <XAxis
                    dataKey="metric"
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

                    <Legend />

                    <Bar
                    dataKey={comparison.rider_a.rider}
                    fill="#dc2626"
                    radius={[8, 8, 0, 0]}
                    />

                    <Bar
                    dataKey={comparison.rider_b.rider}
                    fill="#f97316"
                    radius={[8, 8, 0, 0]}
                    />
                </BarChart>
                </ResponsiveContainer>
            </div>
            </section>

            <section className="mt-8 rounded-2xl border border-red-500/20 bg-red-500/10 p-6">
              <p className="text-sm uppercase tracking-[0.3em] text-red-300">
                RaceMind Insight
              </p>

              <h2 className="mt-3 text-2xl font-black text-white">
                Comparison Summary
              </h2>

              <div className="mt-5 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                <InsightCard
                  label="Higher Points"
                  value={comparison.insights.higher_points}
                />
                <InsightCard
                  label="More Wins"
                  value={comparison.insights.more_wins}
                />
                <InsightCard
                  label="More Podiums"
                  value={comparison.insights.more_podiums}
                />
                <InsightCard
                  label="Better Average Finish"
                  value={comparison.insights.better_average_finish}
                />
                <InsightCard
                  label="Fewer DNFs"
                  value={comparison.insights.fewer_dnfs}
                />
                <InsightCard
                  label="More Consistent Rider"
                  value={comparison.insights.more_consistent_rider}
                />
              </div>

              <p className="mt-6 text-sm leading-6 text-zinc-300">
                Based on this dataset,{" "}
                <span className="font-semibold text-white">
                  {comparison.insights.higher_points}
                </span>{" "}
                leads on total points, while{" "}
                <span className="font-semibold text-white">
                  {comparison.insights.more_consistent_rider}
                </span>{" "}
                appears stronger on consistency using average finish as a simple
                proxy.
              </p>
            </section>
          </>
        )}

        {!comparison && !loadingComparison && !error && (
          <section className="mt-8 rounded-2xl border border-white/10 bg-white/4 p-6">
            <p className="text-zinc-400">
              Select two riders to generate a side-by-side comparison.
            </p>
          </section>
        )}
      </section>
    </main>
  );
}

function InsightCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/10 bg-black/30 p-4">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 font-bold text-white">{value}</p>
    </div>
  );
}