type StatCardProps = {
  label: string;
  value: string | number;
  helper?: string;
};

export default function StatCard({ label, value, helper }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/4 p-5 shadow-xl">
      <p className="text-sm text-zinc-400">{label}</p>
      <p className="mt-2 text-3xl font-black text-white">{value}</p>
      {helper && <p className="mt-2 text-xs text-zinc-500">{helper}</p>}
    </div>
  );
}