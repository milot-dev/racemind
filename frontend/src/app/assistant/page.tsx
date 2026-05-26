"use client";

import { useState } from "react";
import { apiPost } from "@/lib/api";

type ChatResponse = {
  answer: string;
  sources: string[];
};

const exampleQuestions = [
  "What is race pace?",
  "Why is qualifying important in MotoGP?",
  "Explain tire degradation.",
  "What makes a rider consistent?",
  "What is the difference between race pace and qualifying pace?",
];

export default function AssistantPage() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askQuestion(selectedQuestion?: string) {
    const finalQuestion = selectedQuestion ?? question;

    if (!finalQuestion.trim()) {
      setError("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      setError("");
      setResponse(null);
      setQuestion(finalQuestion);

      const data = await apiPost<ChatResponse>("/ai/chat", {
        question: finalQuestion,
      });

      setResponse(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <section className="rounded-3xl border border-red-500/20 bg-linear-to-br from-zinc-950 via-black to-red-950/30 p-8 shadow-2xl">
        <p className="text-sm font-semibold uppercase tracking-[0.3em] text-red-400">
          RAG Racing Assistant
        </p>

        <h1 className="mt-4 text-4xl font-bold text-white md:text-5xl">
          Ask RaceMind AI
        </h1>

        <p className="mt-4 max-w-3xl text-zinc-300">
          Ask MotoGP and motorcycle racing questions grounded in your local
          knowledge base. This is the first real GenAI feature of the MVP.
        </p>

        <div className="mt-8">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Example: What is race pace?"
            className="min-h-35 w-full rounded-2xl border border-zinc-800 bg-black/60 p-4 text-white outline-none transition focus:border-red-500"
          />

          <button
            onClick={() => askQuestion()}
            disabled={loading}
            className="mt-4 rounded-xl bg-red-600 px-6 py-3 font-semibold text-white transition hover:bg-red-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Thinking..." : "Ask Assistant"}
          </button>
        </div>
      </section>

      <section className="mt-8 rounded-2xl border border-zinc-800 bg-zinc-950/80 p-6">
        <h2 className="text-xl font-bold text-white">Example questions</h2>

        <div className="mt-4 flex flex-wrap gap-3">
          {exampleQuestions.map((item) => (
            <button
              key={item}
              onClick={() => askQuestion(item)}
              className="rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-200 transition hover:bg-red-500/20"
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      {error && (
        <section className="mt-8 rounded-2xl border border-red-500/30 bg-red-950/30 p-6 text-red-200">
          {error}
        </section>
      )}

      {response && (
        <section className="mt-8 rounded-2xl border border-zinc-800 bg-black/70 p-6">
          <h2 className="text-2xl font-bold text-white">RaceMind Answer</h2>

          <div className="mt-4 whitespace-pre-line rounded-2xl border border-zinc-800 bg-zinc-950 p-5 leading-7 text-zinc-200">
            {response.answer}
          </div>

          <div className="mt-5">
            <h3 className="font-semibold text-white">Sources</h3>

            {response.sources.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-2">
                {response.sources.map((source) => (
                  <span
                    key={source}
                    className="rounded-full bg-red-500/10 px-3 py-1 text-sm text-red-300"
                  >
                    {source}
                  </span>
                ))}
              </div>
            ) : (
              <p className="mt-2 text-sm text-zinc-400">
                No knowledge base source matched this question.
              </p>
            )}
          </div>
        </section>
      )}
    </main>
  );
}