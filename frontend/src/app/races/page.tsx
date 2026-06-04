"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { apiGet } from "@/lib/api";

type RaceItem = {
  year: number;
  event_name: string;
  circuit?: string | null;
};

type RacesResponse =
  | RaceItem[]
  | {
      races?: RaceItem[];
      data?: RaceItem[];
      count?: number;
    };

function normalizeRacesResponse(data: RacesResponse): RaceItem[] {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data.races)) {
    return data.races;
  }

  if (Array.isArray(data.data)) {
    return data.data;
  }

  return [];
}

export default function RacesPage() {
  const [races, setRaces] = useState<RaceItem[]>([]);
  const [search, setSearch] = useState("");
  const [selectedYear, setSelectedYear] = useState<string>("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const years = useMemo(() => {
    return Array.from(new Set(races.map((race) => race.year)))
      .filter(Boolean)
      .sort((a, b) => b - a);
  }, [races]);

  const filteredRaces = useMemo(() => {
    const query = search.toLowerCase().trim();

    return races.filter((race) => {
      const matchesSearch =
        !query ||
        race.event_name.toLowerCase().includes(query) ||
        String(race.circuit || "").toLowerCase().includes(query);

      const matchesYear =
        selectedYear === "all" || String(race.year) === selectedYear;

      return matchesSearch && matchesYear;
    });
  }, [races, search, selectedYear]);

  useEffect(() => {
    let isMounted = true;

    async function loadRaces() {
      try {
        setLoading(true);
        setError("");

        const data = await apiGet<RacesResponse>("/races");

        const raceList = normalizeRacesResponse(data)
          .filter((race) => race.year && race.event_name)
          .sort((a, b) => {
            if (b.year !== a.year) {
              return b.year - a.year;
            }

            return a.event_name.localeCompare(b.event_name);
          });

        if (isMounted) {
          setRaces(raceList);
        }
      } catch (err) {
        if (isMounted) {
          setError(
            err instanceof Error
              ? err.message
              : "Failed to load races."
          );
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadRaces();

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
          MotoGP Races
        </h1>

        <p className="mt-3 max-w-3xl text-zinc-400">
          Browse all races from the cleaned RaceMind AI dataset. Select a race
          to view podiums, team points, session summaries, and full results.
        </p>

        <div className="mt-8 grid gap-4 rounded-2xl border border-red-500/20 bg-zinc-950 p-5 md:grid-cols-[1fr_220px]">
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search race or circuit..."
            className="w-full rounded-xl border border-zinc-700 bg-black px-4 py-3 text-sm text-white outline-none placeholder:text-zinc-500 focus:border-red-500"
          />

          <select
            value={selectedYear}
            onChange={(event) => setSelectedYear(event.target.value)}
            className="w-full rounded-xl border border-zinc-700 bg-black px-4 py-3 text-sm text-white outline-none focus:border-red-500"
          >
            <option value="all">All years</option>
            {years.map((year) => (
              <option key={year} value={String(year)}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {loading && (
          <p className="mt-8 text-zinc-400">
            Loading races...
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
              Showing {filteredRaces.length} of {races.length} races
            </p>

            {filteredRaces.length > 0 ? (
              <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                {filteredRaces.map((race) => (
                  <Link
                    key={`${race.year}-${race.event_name}-${race.circuit || "unknown"}`}
                    href={`/race/${race.year}/${encodeURIComponent(
                      race.event_name
                    )}`}
                    className="group rounded-2xl border border-red-500/20 bg-zinc-950 p-5 transition hover:border-red-500/50 hover:bg-red-950/20"
                  >
                    <p className="text-sm font-semibold text-red-300">
                      {race.year}
                    </p>

                    <h2 className="mt-2 text-xl font-bold text-white group-hover:text-red-200">
                      {race.event_name}
                    </h2>

                    <p className="mt-2 text-sm text-zinc-500">
                      Circuit: {race.circuit || "Unknown"}
                    </p>

                    <p className="mt-4 text-sm text-zinc-400">
                      View race detail →
                    </p>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-6">
                <p className="text-zinc-400">
                  No races found.
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </main>
  );
}