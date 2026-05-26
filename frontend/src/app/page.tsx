import Link from "next/link";
import { BarChart3, Bot, Brain, Flag, Gauge, Trophy } from "lucide-react";

const features = [
  {
    title: "MotoGP Dashboard",
    description: "Explore real MotoGP race results from recent seasons.",
    icon: BarChart3,
  },
  {
    title: "Rider Comparison",
    description: "Compare riders by wins, podiums, points, consistency, and average finish.",
    icon: Trophy,
  },
  {
    title: "RAG Racing Assistant",
    description: "Ask motorcycle racing questions grounded in a custom knowledge base.",
    icon: Bot,
  },
  {
    title: "AI Commentary Generator",
    description: "Generate dramatic, technical, or social-media-ready racing commentary.",
    icon: Flag,
  },
  {
    title: "ML Performance Predictor",
    description: "Predict whether a rider performance will be Strong, Average, or Poor.",
    icon: Brain,
  },
];

const badges = ["GenAI", "RAG", "Machine Learning", "FastAPI", "Next.js", "MotoGP Data"];

export default function Home() {
  return (
    <main className="min-h-screen px-6 py-16">
      <section className="mx-auto max-w-7xl">
        <div className="grid items-center gap-12 lg:grid-cols-[1.1fr_0.9fr]">
          <div>
            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-300">
              <Gauge size={16} />
              AI Engineering Portfolio Project
            </div>

            <h1 className="max-w-4xl text-5xl font-black tracking-tight text-white md:text-7xl">
              RaceMind <span className="text-red-500">AI</span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-zinc-300">
              GenAI-powered MotoGP intelligence for rider analysis, race commentary,
              and ML-based performance prediction.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              {badges.map((badge) => (
                <span
                  key={badge}
                  className="rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-zinc-300"
                >
                  {badge}
                </span>
              ))}
            </div>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/dashboard"
                className="rounded-xl bg-red-600 px-6 py-3 font-semibold text-white transition hover:bg-red-500"
              >
                Open Dashboard
              </Link>

              <Link
                href="/assistant"
                className="rounded-xl border border-white/15 px-6 py-3 font-semibold text-white transition hover:border-red-400 hover:text-red-300"
              >
                Ask Racing Assistant
              </Link>

              <Link
                href="/commentator"
                className="rounded-xl border border-white/15 px-6 py-3 font-semibold text-white transition hover:border-red-400 hover:text-red-300"
              >
                Generate Commentary
              </Link>
            </div>
          </div>

          <div className="rounded-3xl border border-white/10 bg-white/[0.04] p-6 shadow-2xl">
            <div className="rounded-2xl bg-black/70 p-6">
              <p className="text-sm uppercase tracking-[0.3em] text-red-400">
                Race Intelligence
              </p>
              <h2 className="mt-4 text-3xl font-black text-white">
                Data + GenAI + ML
              </h2>
              <p className="mt-4 text-zinc-400">
                A portfolio-ready platform combining real racing data, analytics,
                retrieval-augmented generation, AI commentary, and model serving.
              </p>

              <div className="mt-8 space-y-3">
                {[
                  "FastAPI backend reads cleaned MotoGP CSV",
                  "Next.js frontend displays dashboards and charts",
                  "RAG assistant answers racing questions",
                  "RandomForest model predicts performance class",
                ].map((item) => (
                  <div
                    key={item}
                    className="rounded-xl border border-white/10 bg-white/[0.03] p-4 text-sm text-zinc-300"
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        <section className="mt-20 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;

            return (
              <div
                key={feature.title}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-6 transition hover:border-red-500/50"
              >
                <Icon className="text-red-500" size={28} />
                <h3 className="mt-5 text-xl font-bold text-white">{feature.title}</h3>
                <p className="mt-3 text-sm leading-6 text-zinc-400">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </section>
      </section>
    </main>
  );
}