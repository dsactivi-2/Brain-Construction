"use client";

import { useState, useEffect } from "react";
import { Brain, Database, HardDrive, Cpu, Server } from "lucide-react";

export default function MemoryPage() {
  const [stats, setStats] = useState<{
    neo4j: { version: string; status: string };
    qdrant: { collections: number; names: string[] };
    ragApi: { status: string; backends: Record<string, string> };
  } | null>(null);

  useEffect(() => {
    async function fetchStats() {
      try {
        const healthRes = await fetch("/api/health");
        const healthData = await healthRes.json();

        const neo4jSvc = healthData.find((s: { name: string }) => s.name === "neo4j");
        const qdrantSvc = healthData.find((s: { name: string }) => s.name === "qdrant");
        const ragSvc = healthData.find((s: { name: string }) => s.name === "rag-api");

        setStats({
          neo4j: {
            version: neo4jSvc?.details?.neo4j_version || "unknown",
            status: neo4jSvc?.status || "unknown",
          },
          qdrant: {
            collections: qdrantSvc?.details?.result?.collections?.length || 0,
            names: qdrantSvc?.details?.result?.collections?.map((c: { name: string }) => c.name) || [],
          },
          ragApi: {
            status: ragSvc?.details?.status || "unknown",
            backends: ragSvc?.details?.backends || {},
          },
        });
      } catch {
        // error
      }
    }
    fetchStats();
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  const LAYERS = [
    {
      id: "S1", name: "Core Memory", icon: Cpu, color: "from-red-500 to-red-700",
      db: "Redis", latency: "<5ms",
      desc: "Immer im Kontext. ~5000 Tokens. [USER], [PROJEKT], [ENTSCHEIDUNGEN], [FEHLER-LOG], [AKTUELLE-ARBEIT]",
      tools: ["core_memory_read", "core_memory_update"],
    },
    {
      id: "S2", name: "Auto-Recall/Capture", icon: HardDrive, color: "from-orange-500 to-orange-700",
      db: "Qdrant + Redis", latency: "~20ms",
      desc: "Automatisch relevante Erinnerungen laden (Recall) und neue speichern (Capture). Priority-Score 1-10.",
      tools: ["memory_search", "memory_store", "memory_list", "memory_get", "memory_forget"],
    },
    {
      id: "S3", name: "HippoRAG 2", icon: Brain, color: "from-amber-500 to-amber-700",
      db: "Neo4j + Qdrant", latency: "~24ms",
      desc: "Wissensgraph mit PersonalizedPageRank + spaCy NER. Entitaeten, Beziehungen, typed Relations.",
      tools: ["hipporag_ingest", "hipporag_retrieve"],
    },
    {
      id: "S4", name: "Agentic RAG", icon: Server, color: "from-green-500 to-green-700",
      db: "Lokal (Prozess)", latency: "0ms",
      desc: "Router entscheidet: welche Schicht, welche Query, wie viel. Evaluator bewertet Ergebnisse.",
      tools: ["rag_route"],
    },
    {
      id: "S5", name: "Learning Graphs", icon: Brain, color: "from-blue-500 to-blue-700",
      db: "Neo4j", latency: "~24ms",
      desc: "Selbst-erweiternd. Pattern-Detection erkennt wiederkehrende Muster. Woechentliche Konsolidierung.",
      tools: ["learning_graph_update", "consolidate", "decay_prune"],
    },
    {
      id: "S6", name: "Recall Memory", icon: Database, color: "from-purple-500 to-purple-700",
      db: "PostgreSQL", latency: "~4ms",
      desc: "Komplette rohe Konversationshistorie. Jede Nachricht, jeder Tool-Call. Nichts geht verloren.",
      tools: ["conversation_search", "conversation_search_date"],
    },
  ];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Memory System</h1>
        <p className="text-sm text-slate-400 mt-1">6-Schichten Gehirn-Architektur</p>
      </div>

      {/* DB Status */}
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database size={16} className="text-green-400" />
              <span className="text-sm font-semibold">Neo4j</span>
            </div>
            <p className="text-xs text-slate-400">v{stats.neo4j.version} &middot; {stats.neo4j.status}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <HardDrive size={16} className="text-blue-400" />
              <span className="text-sm font-semibold">Qdrant</span>
            </div>
            <p className="text-xs text-slate-400">
              {stats.qdrant.collections} Collections
              {stats.qdrant.names.length > 0 && `: ${stats.qdrant.names.join(", ")}`}
            </p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Cpu size={16} className="text-red-400" />
              <span className="text-sm font-semibold">Redis</span>
            </div>
            <p className="text-xs text-slate-400">{stats.ragApi.backends?.redis || "checking..."}</p>
          </div>
          <div className="bg-slate-800 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <Database size={16} className="text-purple-400" />
              <span className="text-sm font-semibold">PostgreSQL</span>
            </div>
            <p className="text-xs text-slate-400">{stats.ragApi.backends?.postgresql || "checking..."}</p>
          </div>
        </div>
      )}

      {/* 6 Layer Cards */}
      <div className="space-y-4">
        {LAYERS.map((layer) => {
          const Icon = layer.icon;
          return (
            <div key={layer.id} className="bg-slate-800 rounded-xl overflow-hidden">
              <div className={`bg-gradient-to-r ${layer.color} px-6 py-3 flex items-center gap-3`}>
                <Icon size={20} />
                <span className="font-mono text-sm bg-white/20 px-2 py-0.5 rounded">{layer.id}</span>
                <span className="font-bold">{layer.name}</span>
                <span className="ml-auto text-xs bg-white/20 px-2 py-0.5 rounded">{layer.db}</span>
              </div>
              <div className="p-6">
                <p className="text-sm text-slate-300 mb-4">{layer.desc}</p>
                <div className="flex items-center gap-4">
                  <div>
                    <span className="text-xs text-slate-500">Tools:</span>
                    <div className="flex gap-1 mt-1 flex-wrap">
                      {layer.tools.map((tool) => (
                        <span key={tool} className="text-xs bg-slate-700 px-2 py-0.5 rounded font-mono">
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="ml-auto text-right">
                    <span className="text-xs text-slate-500">Latency</span>
                    <p className="text-sm font-semibold text-green-400">{layer.latency}</p>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
