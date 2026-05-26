type RiderSelectorProps = {
  label: string;
  riders: string[];
  value: string;
  onChange: (value: string) => void;
};

export default function RiderSelector({
  label,
  riders,
  value,
  onChange,
}: RiderSelectorProps) {
  return (
    <div>
      <label className="mb-2 block text-sm font-medium text-zinc-300">
        {label}
      </label>

      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-xl border border-white/10 bg-black/60 px-4 py-3 text-white outline-none transition focus:border-red-500"
      >
        <option value="">Select rider</option>

        {riders.map((rider) => (
          <option key={rider} value={rider}>
            {rider}
          </option>
        ))}
      </select>
    </div>
  );
}