"use client";

import { useEffect, useState } from "react";
import { apiGet, apiPost } from "@/lib/api";

type PredictionResponse = {
  prediction: string;
  confidence: number;
  probabilities: Record<string, number>;
  explanation?: {
    summary: string;
    top_factors: string[];
    important_features: {
      feature: string;
      importance: number;
    }[];
    model_note: string;
  };
  input?: {
    year: number;
    event_name: string;
    circuit: string;
    rider: string;
    team: string;
    session_type: string;
  };
  message?: string;
};

const defaultEvents = [
  "QAT",
  "SPA",
  "FRA",
  "ITA",
  "GER",
  "NED",
  "AUT",
  "CAT",
  "JPN",
  "AUS",
];

const defaultTeams = [
  "Ducati Lenovo Team",
  "Prima Pramac Racing",
  "Gresini Racing MotoGP",
  "Monster Energy Yamaha MotoGP Team",
  "Red Bull KTM Factory Racing",
  "Aprilia Racing",
  "Pertamina Enduro VR46 Racing Team",
];

export default function PredictPage() {
  const [riders, setRiders] = useState<string[]>([]);
  const [loadingRiders, setLoadingRiders] = useState(true);

  const [year, setYear] = useState(2025);
  const [eventName, setEventName] = useState("QAT");
  const [circuit, setCircuit] = useState("QAT");
  const [rider, setRider] = useState("M. Marquez");
  const [team, setTeam] = useState("Ducati Lenovo Team");
  const [sessionType, setSessionType] = useState("Race");

  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [loadingPrediction, setLoadingPrediction] = useState(false);
  const [error, setError] = useState("");

useEffect(() => {
    async function loadRiders() {
        try {
        setLoadingRiders(true);
        const data = await apiGet<string[]>("/riders");
        setRiders(data);

        if (data.length > 0) {
            setRider((currentRider) =>
            data.includes(currentRider) ? currentRider : data[0]
            );
        }
        } catch {
        setError("Could not load riders. You can still type values manually.");
        } finally {
        setLoadingRiders(false);
        }
    }

    loadRiders();
    }, []);

  async function submitPrediction() {
    if (!eventName.trim() || !circuit.trim() || !rider.trim() || !team.trim()) {
      setError("Please fill all required fields.");
      return;
    }

    try {
      setLoadingPrediction(true);
      setError("");
      setResult(null);

      const data = await apiPost<PredictionResponse>("/ml/predict", {
        year,
        event_name: eventName,
        circuit,
        rider,
        team,
        grid_position: null,
        session_type: sessionType,
      });

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed.");
    } finally {
      setLoadingPrediction(false);
    }
  }

  function getPredictionBadgeClass(prediction: string) {
    if (prediction === "Strong") {
      return "border-green-500/30 bg-green-500/10 text-green-300";
    }

    if (prediction === "Average") {
      return "border-yellow-500/30 bg-yellow-500/10 text-yellow-300";
    }

    if (prediction === "Poor") {
      return "border-red-500/30 bg-red-500/10 text-red-300";
    }

    return "border-zinc-700 bg-zinc-800 text-zinc-300";
  }

  const sortedProbabilities = result
    ? Object.entries(result.probabilities).sort((a, b) => b[1] - a[1])
    : [];

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <section className="rounded-3xl border border-red-500/20 bg-linear-to-br from-zinc-950 via-black to-red-950/30 p-8 shadow-2xl">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-red-400">
          ML Performance Predictor
        </p>

        <h1 className="mt-4 text-4xl font-bold text-white md:text-5xl">
          Predict Rider Performance
        </h1>

        <p className="mt-4 max-w-3xl text-zinc-300">
          Use a trained machine learning model to classify a rider performance
          as Strong, Average, or Poor based on historical MotoGP race data.
        </p>
      </section>

      <section className="mt-8 grid gap-8 lg:grid-cols-[420px_1fr]">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            submitPrediction();
          }}
          className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-6"
        >
          <h2 className="text-2xl font-bold text-white">Prediction Input</h2>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Year</span>
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
            >
              {[2022, 2023, 2024, 2025].map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">
              Event Name
            </span>
            <input
              value={eventName}
              onChange={(e) => {
                setEventName(e.target.value);
                setCircuit(e.target.value);
              }}
              list="event-options"
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="QAT"
            />
            <datalist id="event-options">
              {defaultEvents.map((event) => (
                <option key={event} value={event} />
              ))}
            </datalist>
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Circuit</span>
            <input
              value={circuit}
              onChange={(e) => setCircuit(e.target.value)}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="QAT"
            />
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Rider</span>

            {loadingRiders ? (
              <div className="mt-2 rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-zinc-400">
                Loading riders...
              </div>
            ) : riders.length > 0 ? (
              <select
                value={rider}
                onChange={(e) => setRider(e.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              >
                {riders.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            ) : (
              <input
                value={rider}
                onChange={(e) => setRider(e.target.value)}
                className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
                placeholder="M. Marquez"
              />
            )}
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">Team</span>
            <input
              value={team}
              onChange={(e) => setTeam(e.target.value)}
              list="team-options"
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
              placeholder="Ducati Lenovo Team"
            />
            <datalist id="team-options">
              {defaultTeams.map((teamName) => (
                <option key={teamName} value={teamName} />
              ))}
            </datalist>
          </label>

          <label className="mt-5 block">
            <span className="text-sm font-medium text-zinc-300">
              Session Type
            </span>
            <select
              value={sessionType}
              onChange={(e) => setSessionType(e.target.value)}
              className="mt-2 w-full rounded-xl border border-zinc-800 bg-black/60 px-4 py-3 text-white outline-none focus:border-red-500"
            >
              <option value="Race">Race</option>
              <option value="Sprint">Sprint</option>
            </select>
          </label>

          <button
            type="submit"
            disabled={loadingPrediction}
            className="mt-6 w-full rounded-xl bg-red-600 px-6 py-3 font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loadingPrediction ? "Predicting..." : "Predict Performance"}
          </button>

          {error && (
            <p className="mt-4 rounded-xl border border-red-500/30 bg-red-950/30 p-3 text-sm text-red-200">
              {error}
            </p>
          )}
        </form>

        <section className="rounded-2xl border border-zinc-800 bg-black/70 p-6">
          <h2 className="text-2xl font-bold text-white">Prediction Result</h2>

          {!result && !loadingPrediction && (
            <div className="mt-8 rounded-2xl border border-dashed border-zinc-800 p-8 text-zinc-400">
              Submit race context to get a machine learning prediction.
            </div>
          )}

          {loadingPrediction && (
            <div className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950 p-8 text-zinc-300">
              RaceMind AI is running the performance classifier...
            </div>
          )}

          {result && (
            <div className="mt-8">
              <div
                className={`inline-flex rounded-full border px-5 py-2 text-lg font-bold ${getPredictionBadgeClass(
                  result.prediction
                )}`}
              >
                {result.prediction}
              </div>

              {result?.explanation && (
              <div className="mt-6 rounded-2xl border border-red-500/20 bg-zinc-950 p-5">
                <h3 className="text-lg font-bold text-white">
                  Prediction Explanation
                </h3>

                <p className="mt-3 text-sm leading-6 text-zinc-300">
                  {result.explanation.summary}
                </p>

                {result.explanation.top_factors?.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm font-semibold text-zinc-200">
                      Main factors:
                    </p>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {result.explanation.top_factors.map((factor: string) => (
                        <span
                          key={factor}
                          className="rounded-full border border-red-500/30 bg-red-500/10 px-3 py-1 text-xs text-red-200"
                        >
                          {factor}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {result.explanation.important_features?.length > 0 && (
                  <div className="mt-5">
                    <p className="text-sm font-semibold text-zinc-200">
                      Feature importance:
                    </p>

                    <div className="mt-3 space-y-2">
                      {result.explanation.important_features.map(
                        (item: { feature: string; importance: number }) => (
                          <div
                            key={item.feature}
                            className="flex items-center justify-between rounded-lg border border-zinc-800 bg-black/40 px-3 py-2 text-sm"
                          >
                            <span className="text-zinc-300">
                              {item.feature}
                            </span>
                            <span className="font-semibold text-red-300">
                              {(item.importance * 100).toFixed(1)}%
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  </div>
                )}

                <p className="mt-4 text-xs text-zinc-500">
                  {result.explanation.model_note}
                </p>
              </div>
            )}

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
                  <p className="text-sm text-zinc-400">Confidence</p>
                  <p className="mt-2 text-4xl font-bold text-white">
                    {Math.round(result.confidence * 100)}%
                  </p>
                </div>

                <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
                  <p className="text-sm text-zinc-400">Model Type</p>
                  <p className="mt-2 text-xl font-bold text-white">
                    RandomForest Classifier
                  </p>
                </div>
              </div>

              <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
                <h3 className="text-lg font-bold text-white">
                  Probability Breakdown
                </h3>

                <div className="mt-5 space-y-4">
                  {sortedProbabilities.map(([label, value]) => (
                    <div key={label}>
                      <div className="mb-2 flex justify-between text-sm">
                        <span className="font-medium text-zinc-200">
                          {label}
                        </span>
                        <span className="text-zinc-400">
                          {Math.round(value * 100)}%
                        </span>
                      </div>

                      <div className="h-3 overflow-hidden rounded-full bg-zinc-800">
                        <div
                          className="h-full rounded-full bg-red-600"
                          style={{
                            width: `${Math.round(value * 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {result.input && (
                <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-950 p-5">
                  <h3 className="text-lg font-bold text-white">Input Used</h3>

                  <div className="mt-4 grid gap-3 text-sm text-zinc-300 md:grid-cols-2">
                    <p>
                      <span className="text-zinc-500">Year:</span>{" "}
                      {result.input.year}
                    </p>
                    <p>
                      <span className="text-zinc-500">Event:</span>{" "}
                      {result.input.event_name}
                    </p>
                    <p>
                      <span className="text-zinc-500">Circuit:</span>{" "}
                      {result.input.circuit}
                    </p>
                    <p>
                      <span className="text-zinc-500">Rider:</span>{" "}
                      {result.input.rider}
                    </p>
                    <p>
                      <span className="text-zinc-500">Team:</span>{" "}
                      {result.input.team}
                    </p>
                    <p>
                      <span className="text-zinc-500">Session:</span>{" "}
                      {result.input.session_type}
                    </p>
                  </div>
                </div>
              )}

              <p className="mt-6 rounded-2xl border border-yellow-500/20 bg-yellow-500/10 p-4 text-sm leading-6 text-yellow-100">
                {result.message ??
                  "This is a simple ML prediction based on historical MotoGP results. It is for portfolio/demo purposes, not an official race forecast."}
              </p>
            </div>
          )}
        </section>
      </section>
    </main>
  );
}