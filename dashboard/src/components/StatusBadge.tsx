interface Props {
  status: string;
  size?: "sm" | "md";
}

const COLORS: Record<string, string> = {
  healthy: "bg-green-500",
  connected: "bg-green-500",
  ok: "bg-green-500",
  idle: "bg-slate-400",
  working: "bg-blue-500",
  blocked: "bg-red-500",
  degraded: "bg-amber-500",
  down: "bg-red-600",
  offline: "bg-slate-600",
  unknown: "bg-slate-500",
  done: "bg-green-500",
  in_progress: "bg-blue-500",
  review: "bg-amber-500",
  backlog: "bg-slate-400",
};

export default function StatusBadge({ status, size = "sm" }: Props) {
  const color = COLORS[status] || "bg-slate-500";
  const dotSize = size === "sm" ? "w-2 h-2" : "w-3 h-3";

  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={`${dotSize} rounded-full ${color} animate-pulse`} />
      <span className="text-xs capitalize">{status.replace("_", " ")}</span>
    </span>
  );
}
