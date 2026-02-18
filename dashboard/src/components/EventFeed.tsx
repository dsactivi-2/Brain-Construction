"use client";

import { useState, useEffect } from "react";
import { EventBusMessage } from "@/lib/types";
import { Radio, Bug, Lightbulb, TrendingUp, AlertTriangle } from "lucide-react";

const CHANNEL_CONFIG: Record<string, { icon: typeof Bug; color: string; bg: string }> = {
  bugs: { icon: Bug, color: "text-red-400", bg: "bg-red-500/10" },
  decisions: { icon: Lightbulb, color: "text-amber-400", bg: "bg-amber-500/10" },
  progress: { icon: TrendingUp, color: "text-green-400", bg: "bg-green-500/10" },
  blocker: { icon: AlertTriangle, color: "text-orange-400", bg: "bg-orange-500/10" },
};

// Simulated event feed (in production: Redis Pub/Sub via WebSocket)
const DEMO_EVENTS: EventBusMessage[] = [
  { id: "1", channel: "progress", sender: "devops", message: "Docker Services deployed: alle 8 healthy", timestamp: "2026-02-18T00:39:00Z" },
  { id: "2", channel: "progress", sender: "coder", message: "PPR + spaCy NER Upgrade committed (188d81a)", timestamp: "2026-02-17T14:30:00Z" },
  { id: "3", channel: "decisions", sender: "architekt", message: "v3.0 Profile mit memory_strategie + lade_strategie", timestamp: "2026-02-17T15:00:00Z" },
  { id: "4", channel: "progress", sender: "reviewer", message: "11 merged profile.json deployed (f4b0c62)", timestamp: "2026-02-17T22:41:00Z" },
  { id: "5", channel: "progress", sender: "designer", message: "Kanban Dashboard gestartet (Next.js)", timestamp: "2026-02-18T01:00:00Z" },
  { id: "6", channel: "decisions", sender: "berater", message: "Memory-Manager Agent (H8) hinzugefuegt — 11 Agenten total", timestamp: "2026-02-17T20:00:00Z" },
];

export default function EventFeed() {
  const [events, setEvents] = useState<EventBusMessage[]>(DEMO_EVENTS);

  useEffect(() => {
    // In production: WebSocket to Redis Pub/Sub
    const interval = setInterval(() => {
      // Simulated new events
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-800/50 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-4">
        <Radio size={16} className="text-blue-400" />
        <h3 className="font-semibold text-sm">Event-Bus Feed</h3>
        <span className="text-xs text-slate-500">Redis Pub/Sub</span>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {events.map((event) => {
          const config = CHANNEL_CONFIG[event.channel] || CHANNEL_CONFIG.progress;
          const Icon = config.icon;
          const time = new Date(event.timestamp).toLocaleTimeString("de-DE", {
            hour: "2-digit",
            minute: "2-digit",
          });

          return (
            <div
              key={event.id}
              className={`${config.bg} rounded-lg p-3 border border-transparent hover:border-slate-600 transition-colors`}
            >
              <div className="flex items-start gap-2">
                <Icon size={14} className={`${config.color} mt-0.5 shrink-0`} />
                <div className="flex-1 min-w-0">
                  <p className="text-xs">{event.message}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500">@{event.sender}</span>
                    <span className="text-xs text-slate-600">{time}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${config.bg} ${config.color}`}>
                      #{event.channel}
                    </span>
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
