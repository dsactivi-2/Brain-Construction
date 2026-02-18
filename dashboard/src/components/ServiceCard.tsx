import StatusBadge from "./StatusBadge";
import { Database, Server, Cpu, HardDrive } from "lucide-react";

interface Props {
  name: string;
  port: number | string;
  schicht: string;
  status: string;
  responseTime?: number;
}

const ICONS: Record<string, typeof Database> = {
  "neo4j": Database,
  "qdrant": HardDrive,
  "redis": Cpu,
  "recall-db": Database,
  "rag-api": Server,
  "doc-scanner": Server,
  "hipporag": Server,
  "learning-graphs": Server,
};

export default function ServiceCard({ name, port, schicht, status, responseTime }: Props) {
  const Icon = ICONS[name] || Server;
  const borderColor =
    status === "healthy" ? "border-green-500/30" :
    status === "degraded" ? "border-amber-500/30" :
    status === "down" ? "border-red-500/30" : "border-slate-600";

  return (
    <div className={`bg-slate-800 rounded-xl p-4 border ${borderColor}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon size={18} className="text-slate-400" />
          <span className="font-semibold text-sm">{name}</span>
        </div>
        <StatusBadge status={status} />
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span>:{port}</span>
        <span className="bg-slate-700 px-2 py-0.5 rounded">{schicht}</span>
      </div>
      {responseTime !== undefined && (
        <div className="mt-2 text-xs text-slate-500">
          {responseTime}ms
        </div>
      )}
    </div>
  );
}
