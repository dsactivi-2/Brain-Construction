"use client";

import { useState, useEffect } from "react";
import ServiceCard from "@/components/ServiceCard";
import { RefreshCw } from "lucide-react";

interface ServiceStatus {
  name: string;
  port: number;
  schicht: string;
  status: string;
  responseTime: number;
}

const LAYER_MAP: Record<string, { name: string; desc: string }> = {
  "S1": { name: "Core Memory", desc: "Redis — immer im Kontext, <5ms" },
  "S2+S3": { name: "Vektor + Graph", desc: "Qdrant — Embeddings fuer S2 + S3" },
  "S3+S5": { name: "Wissensgraph", desc: "Neo4j — HippoRAG + Learning Graphs" },
  "S4": { name: "Agentic RAG", desc: "Router — intelligente Suchsteuerung" },
  "S3": { name: "HippoRAG", desc: "Entity Extraction + PPR" },
  "S6": { name: "Recall Memory", desc: "PostgreSQL — komplette Historie" },
  "-": { name: "Service", desc: "Kein Brain-Layer" },
};

export default function HealthPage() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [loading, setLoading] = useState(false);
  const [lastCheck, setLastCheck] = useState<string>("");

  async function fetchHealth() {
    setLoading(true);
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      setServices(data);
      setLastCheck(new Date().toLocaleTimeString("de-DE"));
    } catch {
      // error
    }
    setLoading(false);
  }

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const healthyCount = services.filter((s) => s.status === "healthy").length;
  const downCount = services.filter((s) => s.status === "down").length;

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold">Service Health</h1>
          <p className="text-sm text-slate-400 mt-1">
            {healthyCount} healthy, {downCount} down &middot; Letzter Check: {lastCheck}
          </p>
        </div>
        <button
          onClick={fetchHealth}
          disabled={loading}
          className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Overview Bar */}
      <div className="bg-slate-800 rounded-xl p-4 mb-8">
        <div className="flex gap-1 h-3 rounded-full overflow-hidden">
          {services.map((svc) => (
            <div
              key={svc.name}
              className={`flex-1 ${
                svc.status === "healthy" ? "bg-green-500" :
                svc.status === "degraded" ? "bg-amber-500" :
                svc.status === "down" ? "bg-red-500" : "bg-slate-600"
              }`}
              title={`${svc.name}: ${svc.status}`}
            />
          ))}
        </div>
        <div className="flex justify-between mt-2 text-xs text-slate-500">
          {services.map((svc) => (
            <span key={svc.name}>{svc.name}</span>
          ))}
        </div>
      </div>

      {/* Service Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {services.map((svc) => (
          <ServiceCard
            key={svc.name}
            name={svc.name}
            port={svc.port}
            schicht={svc.schicht}
            status={svc.status}
            responseTime={svc.responseTime}
          />
        ))}
      </div>

      {/* Layer Details */}
      <h2 className="text-lg font-semibold mb-4">Brain Layers</h2>
      <div className="grid grid-cols-3 gap-4">
        {Object.entries(LAYER_MAP).map(([key, layer]) => {
          const layerServices = services.filter((s) => s.schicht === key);
          const allHealthy = layerServices.every((s) => s.status === "healthy");
          const anyDown = layerServices.some((s) => s.status === "down");

          return (
            <div key={key} className="bg-slate-800 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className={`w-2 h-2 rounded-full ${
                  layerServices.length === 0 ? "bg-slate-500" :
                  allHealthy ? "bg-green-500" :
                  anyDown ? "bg-red-500" : "bg-amber-500"
                }`} />
                <span className="text-xs bg-slate-700 px-2 py-0.5 rounded font-mono">{key}</span>
                <span className="font-semibold text-sm">{layer.name}</span>
              </div>
              <p className="text-xs text-slate-400">{layer.desc}</p>
              {layerServices.length > 0 && (
                <div className="mt-2 text-xs text-slate-500">
                  Services: {layerServices.map((s) => s.name).join(", ")}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
