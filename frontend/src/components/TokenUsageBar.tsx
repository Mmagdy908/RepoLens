"use client";

interface TokenUsageBarProps {
  used: number;
  budget: number;
}

export default function TokenUsageBar({ used, budget }: TokenUsageBarProps) {
  const percentage = budget > 0 ? Math.min((used / budget) * 100, 100) : 0;

  const barColour =
    percentage >= 90
      ? "bg-red-500"
      : percentage >= 70
      ? "bg-yellow-500"
      : "bg-green-500";

  return (
    <div className="w-full space-y-1">
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>Token usage</span>
        <span>
          {used.toLocaleString()} / {budget.toLocaleString()} tokens
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-700">
        <div
          className={`h-full rounded-full transition-all duration-500 ${barColour}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}
