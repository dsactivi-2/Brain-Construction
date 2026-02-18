"use client";

import AgentCard from "@/components/AgentCard";
import { AGENTS } from "@/lib/types";

export default function AgentsPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Agent Monitor</h1>
        <p className="text-sm text-slate-400 mt-1">11 Agents, sortiert nach Hierarchie</p>
      </div>

      {/* Hierarchy Visualization */}
      <div className="bg-slate-800 rounded-xl p-6 mb-8">
        <h2 className="text-sm font-semibold text-slate-400 mb-4">Hierarchie</h2>
        <div className="flex items-end gap-1 h-32">
          {AGENTS.map((agent) => (
            <div key={agent.id} className="flex-1 flex flex-col items-center gap-1">
              <span className="text-xs text-slate-500">H{agent.hierarchie}</span>
              <div
                className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-sm"
                style={{ height: `${(agent.hierarchie / 10) * 100}%` }}
              />
              <span className="text-[10px] text-slate-400 truncate w-full text-center">
                {agent.name.split("-")[0]}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Conflict Resolution */}
      <div className="bg-slate-800 rounded-xl p-4 mb-8">
        <h2 className="text-sm font-semibold text-slate-400 mb-2">Conflict Resolution</h2>
        <div className="flex items-center gap-1 flex-wrap text-xs">
          {AGENTS.map((agent, i) => (
            <span key={agent.id} className="flex items-center gap-1">
              <span className="bg-slate-700 px-2 py-1 rounded">
                {agent.name} ({agent.hierarchie})
              </span>
              {i < AGENTS.length - 1 && <span className="text-slate-500">&gt;</span>}
            </span>
          ))}
        </div>
      </div>

      {/* Agent Cards Grid */}
      <div className="grid grid-cols-3 gap-4">
        {AGENTS.map((agent) => (
          <AgentCard key={agent.id} agent={agent} />
        ))}
      </div>

      {/* Tools Matrix */}
      <h2 className="text-lg font-semibold mt-8 mb-4">Tools pro Agent</h2>
      <div className="bg-slate-800 rounded-xl overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-slate-700">
              <th className="text-left px-3 py-2">Agent</th>
              <th className="px-2 py-2">S1</th>
              <th className="px-2 py-2">S2</th>
              <th className="px-2 py-2">S3</th>
              <th className="px-2 py-2">S4</th>
              <th className="px-2 py-2">S5</th>
              <th className="px-2 py-2">S6</th>
              <th className="px-2 py-2">Total</th>
            </tr>
          </thead>
          <tbody>
            {AGENTS.map((agent) => {
              const hasS5 = agent.id === "memory-manager" || agent.id === "berater";
              return (
                <tr key={agent.id} className="border-t border-slate-700">
                  <td className="px-3 py-2 font-medium">{agent.name}</td>
                  <td className="px-2 py-2 text-center text-green-400">&#10003;</td>
                  <td className="px-2 py-2 text-center text-green-400">&#10003;</td>
                  <td className="px-2 py-2 text-center text-green-400">&#10003;</td>
                  <td className="px-2 py-2 text-center text-green-400">&#10003;</td>
                  <td className="px-2 py-2 text-center">
                    {hasS5 ? (
                      <span className="text-green-400">&#10003;</span>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                  <td className="px-2 py-2 text-center text-green-400">&#10003;</td>
                  <td className="px-2 py-2 text-center font-semibold">{agent.toolsCount}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
