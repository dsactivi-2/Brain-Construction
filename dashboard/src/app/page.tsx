"use client";

import { useState, useEffect } from "react";
import ServiceCard from "@/components/ServiceCard";
import AgentCard from "@/components/AgentCard";
import EventFeed from "@/components/EventFeed";
import { AGENTS } from "@/lib/types";
import { Activity, Users, Database, CheckCircle } from "lucide-react";

interface ServiceStatus {
  name: string;
  port: number;
  schicht: string;
  status: string;
  responseTime: number;
}

export default function DashboardPage() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [taskStats, setTaskStats] = useState({ backlog: 0, in_progress: 0, review: 0, done: 0 });

  useEffect(() => {
    async function fetchData() {
      try {
        const [healthRes, tasksRes] = await Promise.all([
          fetch("/api/health"),
          fetch("/api/tasks"),
        ]);
        const healthData = await healthRes.json();
        const tasksData = await tasksRes.json();
        setServices(healthData);
        const stats = { backlog: 0, in_progress: 0, review: 0, done: 0 };
        tasksData.forEach((t: { status: keyof typeof stats }) => {
          if (stats[t.status] !== undefined) stats[t.status]++;
        });
        setTaskStats(stats);
      } catch {
        // Services not reachable
      }
    }
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const healthyCount = services.filter((s) => s.status === "healthy").length;
  const totalServices = services.length || 7;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">Cloud Code Team 02.26 — Brain System v3.0</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="bg-green-500/10 p-3 rounded-lg">
            <Activity size={20} className="text-green-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">{healthyCount}/{totalServices}</p>
            <p className="text-xs text-slate-400">Services Healthy</p>
          </div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="bg-blue-500/10 p-3 rounded-lg">
            <Users size={20} className="text-blue-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">11</p>
            <p className="text-xs text-slate-400">Agents Deployed</p>
          </div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="bg-purple-500/10 p-3 rounded-lg">
            <Database size={20} className="text-purple-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">6</p>
            <p className="text-xs text-slate-400">Brain Layers</p>
          </div>
        </div>
        <div className="bg-slate-800 rounded-xl p-4 flex items-center gap-4">
          <div className="bg-amber-500/10 p-3 rounded-lg">
            <CheckCircle size={20} className="text-amber-400" />
          </div>
          <div>
            <p className="text-2xl font-bold">
              {taskStats.done}/{taskStats.backlog + taskStats.in_progress + taskStats.review + taskStats.done}
            </p>
            <p className="text-xs text-slate-400">Tasks Done</p>
          </div>
        </div>
      </div>

      {/* Services Grid */}
      <h2 className="text-lg font-semibold mb-4">Docker Services</h2>
      <div className="grid grid-cols-4 gap-3 mb-8">
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

      {/* Agents + Event Feed */}
      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2">
          <h2 className="text-lg font-semibold mb-4">Agents (Top 6)</h2>
          <div className="grid grid-cols-2 gap-3">
            {AGENTS.slice(0, 6).map((agent) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>
        </div>
        <div>
          <EventFeed />
        </div>
      </div>
    </div>
  );
}
