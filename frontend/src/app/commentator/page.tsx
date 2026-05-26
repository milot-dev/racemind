"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

type CommentaryResponse = {
  commentary: string;
  style: string;
  rider: string;
  race: string;
  used_openai: boolean;
};

const styles = [
  "dramatic commentator",
  "technical race engineer",
  "documentary narrator",
  "social media caption",
  "beginner-friendly explanation",
];

export default function CommentatorPage() {
  const [rider, setRider] = useState("Marc Marquez");
  const [race, setRace] = useState("Sachsenring");
  const [scenario, setScenario] = useState(
    "Started from P8 and finished P2 after a strong comeback"
  );
  const [style, setStyle] = useState("dramatic commentator");
  const [durationSeconds, setDurationSeconds] = useState(45);

  const [result, setResult] = useState<CommentaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  async function generateCommentary() {
    if (!rider.trim() || !race.trim() || !scenario.trim()) {
      setError("Please fill rider, race, and scenario.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setCopied(false);
      setResult(null);

      const data = await apiPost<CommentaryResponse>("/ai/commentary", {
        rider,
        race,
        scenario,
        style,
        duration_seconds: durationSeconds,
      });

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  async function copyToClipboard() {
    if (!result?.commentary) return;

    await navigator.clipboard.writeText(result.commentary);
    setCopied(true);
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <section className="rounded-3xl border border-red-500/20 bg-linear-to-br from-zinc-950 via-black to-red-950/30 p-8 shadow-2xl">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-red-400">
          AI Commentary Generator
        </p>

        <h1 className="mt-4 text-4xl font-bold text-white md:text-5xl">
          Generate MotoGP Commentary
        </h1>

        <p className="mt-4 max-w-3xl text-zinc-300">
          Turn a race scenario into dramatic, technical, documentary, social
          media, or beginner-friendly MotoGP commentary.
        </p>
      </section>

      <section className="mt-8 grid gap-8 lg:grid-cols-[420px_1fr]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            generateCommentary();
          }}
          className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-6"
        >
          <h2 className="text-2xl font-bold text-white">Scenario Input</h2>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Rider</span>
            <input
              value={rider}
              onChange={(e) => setRider(e.target.value)}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="Marc Marquez"
            />
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">
              Race / Event
            </span>
            <input
              value={race}
              onChange={(e) => setRace(e.target.value)}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="Sachsenring"
            />
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Scenario</span>
            <textarea
              value={scenario}
              onChange={(e) => setScenario(e.target.value)}
              className="mt-2 min-h-35 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="Started from P8 and finished P2 after a strong comeback"
            />
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Style</span>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
            >
              {styles.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">
              Duration seconds
            </span>
            <input
              type="number"
              min={15}
              max={120}
              value={durationSeconds}
              onChange={(e) => setDurationSeconds(Number(e.target.value))}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full rounded-xl bg-red-600 px-6 py-3 font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Generating..." : "Generate Commentary"}
          </button>

          {error && (
            <p className="mt-4 rounded-xl border border-red-500/30 bg-red-950/30 p-3 text-sm text-red-200">
              {error}
            </p>
          )}
        </form>

        <section className="rounded-2xl border border-zinc-800 bg-black/70 p-6">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
            <div>
              <h2 className="text-2xl font-bold text-white">
                Generated Commentary
              </h2>
              <p className="mt-1 text-sm text-zinc-400">
                Result appears here after generation.
              </p>
            </div>

            {result && (
              <button
                onClick={copyToClipboard}
                className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-semibold text-red-200 transition hover:bg-red-500/20"
              >
                {copied ? "Copied!" : "Copy"}
              </button>
            )}
          </div>

          {!result && !loading && (
            <div className="mt-8 rounded-2xl border border-dashed border-zinc-800 p-8 text-zinc-400">
              Fill in a race scenario and generate your first RaceMind AI
              commentary.
            </div>
          )}

          {loading && (
            <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-8 text-zinc-300">
              RaceMind AI is preparing the commentary...
            </div>
          )}

          {result && (
            <div className="mt-8">
              <div className="flex flex-wrap gap-2">
                <span className="rounded-full bg-red-500/10 px-3 py-1 text-sm text-red-300">
                  {result.rider}
                </span>
                <span className="rounded-full bg-orange-500/10 px-3 py-1 text-sm text-orange-300">
                  {result.race}
                </span>
                <span className="rounded-full bg-zinc-800 px-3 py-1 text-sm text-zinc-300">
                  {result.style}
                </span>
                <span className="rounded-full bg-zinc-800 px-3 py-1 text-sm text-zinc-300">
                  {result.used_openai ? "OpenAI" : "Local fallback"}
                </span>
              </div>

              <div className="mt-5 whitespace-pre-line rounded-2xl border border-zinc-800 bg-zinc-950 p-6 text-lg leading-8 text-zinc-100">
                {result.commentary}
              </div>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}