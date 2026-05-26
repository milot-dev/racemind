type BestEvent = {
  year: number;
  event_name: string;
  session_type: string;
  finish_position: number;
} | null;

export type RiderStats = {
  rider: string;
  team_names: string[];
  total_entries: number;
  race_entries: number;
  sprint_entries: number;
  wins: number;
  podiums: number;
  top_10s: number;
  dnfs: number;
  average_finish: number | null;
  average_grid: number | null;
  total_points: number;
  best_finish: number | null;
  worst_finish: number | null;
  best_event: BestEvent;
};

type RiderStatsCardProps = {
  stats: RiderStats;
};

export default function RiderStatsCard({ stats }: RiderStatsCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/4 p-6 shadow-xl">
      <div>
        <p className="text-sm uppercase tracking-[0.25em] text-red-400">
          Rider Profile
        </p>
        <h2 className="mt-2 text-3xl font-black text-white">{stats.rider}</h2>

        <p className="mt-3 text-sm text-zinc-400">
          Teams: {stats.team_names.slice(0, 3).join(", ")}
          {stats.team_names.length > 3 ? "..." : ""}
        </p>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-3">
        <MiniStat label="Points" value={stats.total_points} />
        <MiniStat label="Wins" value={stats.wins} />
        <MiniStat label="Podiums" value={stats.podiums} />
        <MiniStat label="Top 10s" value={stats.top_10s} />
        <MiniStat label="DNFs" value={stats.dnfs} />
        <MiniStat
          label="Avg Finish"
          value={stats.average_finish ?? "N/A"}
        />
      </div>

      {stats.best_event && (
        <div className="mt-6 rounded-xl border border-white/10 bg-black/30 p-4">
          <p className="text-sm text-zinc-400">Best event</p>
          <p className="mt-1 font-semibold text-white">
            P{stats.best_event.finish_position} — {stats.best_event.event_name}{" "}
            {stats.best_event.year}
          </p>
          <p className="text-xs text-zinc-500">{stats.best_event.session_type}</p>
        </div>
      )}
    </div>
  );
}

function MiniStat({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-xl bg-black/30 p-4">
      <p className="text-xs text-zinc-500">{label}</p>
      <p className="mt-1 text-xl font-bold text-white">{value}</p>
    </div>
  );
}