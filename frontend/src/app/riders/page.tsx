"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";

type RidersApiResponse =
  | string[]
  | {
      riders?: string[];
      data?: string[];
    };

function normalizeRidersResponse(data: RidersApiResponse): string[] {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.riders)) {
    return data.riders;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  return [];
}

export default function RidersPage() {
  const [riders, setRiders] = useState<string[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const filteredRiders = useMemo(() => {
    const query = search.toLowerCase().trim();

    if (!query) {
      return riders;
    }

    return riders.filter((rider) =>
      rider.toLowerCase().includes(query)
    );
  }, [riders, search]);

  useEffect(() => {
    let isMounted = true;

    async function loadRiders() {
      try {
        setLoading(true);
        setError("");

        const data = await apiGet<RidersApiResponse>("/riders");
        const riderList = normalizeRidersResponse(data)
          .filter(Boolean)
          .sort((a, b) => a.localeCompare(b));

        if (isMounted) {
          setRiders(riderList);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load riders."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadRiders();

    return () => {
      isMounted = false;
    };
  }, []);

  return (
    <main className="min-h-screen bg-black px-6 py-10 text-white">
      <div className="mx-auto max-w-7xl">
        <p className="text-sm uppercase tracking-[0.3em] text-red-400">
          RaceMind AI
        </p>

        <h1 className="mt-3 text-4xl font-black">
          MotoGP Riders
        </h1>

        <p className="mt-3 max-w-3xl text-zinc-400">
          Browse all riders from the cleaned RaceMind AI dataset. Select a rider
          to open their profile, team history, season trends, and recent results.
        </p>

        <div className="mt-8 rounded-2xl border border-red-500/20 bg-zinc-950 p-5">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search rider..."
            className="w-full rounded-xl border border-zinc-700 bg-black px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-500 focus:border-red-500"
          />
        </div>

        {loading && (
          <p className="mt-8 text-zinc-400">
            Loading riders...
          </p>
        )}

        {!loading && error && (
          <div className="mt-8 rounded-2xl border border-red-500/20 bg-red-950/20 p-6">
            <p className="text-red-300">
              {error}
            </p>
          </div>
        )}

        {!loading && !error && (
          <>
            <p className="mt-6 text-sm text-zinc-400">
              Showing {filteredRiders.length} of {riders.length} riders
            </p>

            {filteredRiders.length > 0 ? (
              <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {filteredRiders.map((rider) => (
                  <Link
                    key={rider}
                    href={`/rider/${encodeURIComponent(rider)}`}
                    className="group rounded-2xl border border-red-500/20 bg-zinc-950 p-5 transition hover:border-red-500/50 hover:bg-red-950/20"
                  >
                    <p className="text-lg font-bold text-white group-hover:text-red-200">
                      {rider}
                    </p>

                    <p className="mt-2 text-sm text-zinc-500">
                      View rider profile →
                    </p>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
                <p className="text-zinc-400">
                  No riders found.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}