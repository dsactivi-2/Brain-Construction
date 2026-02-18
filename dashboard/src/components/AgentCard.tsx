import StatusBadge from "./StatusBadge";
import { Agent } from "@/lib/types";

interface Props {
  agent: Agent;
}

const HIERARCHY_COLORS: Record<number, string> = {
  10: "from-purple-600 to-purple-800",
  9: "from-blue-600 to-blue-800",
  8: "from-cyan-600 to-cyan-800",
  7: "from-green-600 to-green-800",
  6: "from-emerald-600 to-emerald-800",
  5: "from-teal-600 to-teal-800",
  4: "from-amber-600 to-amber-800",
  3: "from-orange-600 to-orange-800",
  2: "from-rose-600 to-rose-800",
  1: "from-slate-600 to-slate-800",
};

export default function AgentCard({ agent }: Props) {
  const gradient = HIERARCHY_COLORS[agent.hierarchie] || "from-slate-600 to-slate-800";

  return (
    <div className="bg-slate-800 rounded-xl overflow-hidden">
      <div className={`bg-gradient-to-r ${gradient} px-4 py-2 flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          <span className="text-xs bg-white/20 px-1.5 py-0.5 rounded font-mono">
            H{agent.hierarchie}
          </span>
          <span className="font-bold text-sm">{agent.name}</span>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      <div className="p-4">
        <p className="text-xs text-slate-400 mb-2">{agent.rolle}</p>
        <div className="flex items-center justify-between text-xs">
          <span className="text-slate-500">{agent.modell}</span>
          <span className="bg-slate-700 px-2 py-0.5 rounded">
            {agent.toolsCount} Tools
          </span>
        </div>
        {agent.currentTask && (
          <div className="mt-2 text-xs bg-blue-500/10 border border-blue-500/20 rounded px-2 py-1 text-blue-300">
            {agent.currentTask}
          </div>
        )}
      </div>
    </div>
  );
}
