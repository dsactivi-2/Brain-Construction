// === Agent Team Dashboard Types ===

export interface Agent {
  id: string;
  name: string;
  hierarchie: number;
  modell: string;
  rolle: string;
  status: "idle" | "working" | "blocked" | "offline";
  currentTask?: string;
  toolsCount: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  assignedAgent?: string;
  priority: number;
  status: "backlog" | "in_progress" | "review" | "done";
  createdAt: string;
  updatedAt: string;
}

export interface ServiceHealth {
  name: string;
  port: number | string;
  status: "healthy" | "degraded" | "down" | "unknown";
  schicht: string;
  responseTime?: number;
  details?: Record<string, string>;
}

export interface BrainStats {
  neo4j: { nodes: number; relationships: number; labels: string[] };
  qdrant: { collections: number; vectors: number };
  redis: { keys: number; memory: string; uptime: string };
  postgresql: { conversations: number; size: string };
}

export interface EventBusMessage {
  id: string;
  channel: "bugs" | "decisions" | "progress" | "blocker";
  sender: string;
  message: string;
  timestamp: string;
}

export type KanbanColumn = "backlog" | "in_progress" | "review" | "done";

export const KANBAN_COLUMNS: { id: KanbanColumn; title: string; color: string }[] = [
  { id: "backlog", title: "Backlog", color: "bg-slate-500" },
  { id: "in_progress", title: "In Progress", color: "bg-blue-500" },
  { id: "review", title: "Review", color: "bg-amber-500" },
  { id: "done", title: "Done", color: "bg-green-500" },
];

export const AGENTS: Agent[] = [
  { id: "berater", name: "BERATER", hierarchie: 10, modell: "Opus", rolle: "Orchestrator", status: "idle", toolsCount: 13 },
  { id: "architekt", name: "ARCHITEKT", hierarchie: 9, modell: "Opus", rolle: "System-Design", status: "idle", toolsCount: 12 },
  { id: "memory-manager", name: "MEMORY-MANAGER", hierarchie: 8, modell: "Sonnet/Opus", rolle: "Brain-System", status: "idle", toolsCount: 15 },
  { id: "coder", name: "CODER", hierarchie: 7, modell: "Sonnet/Opus", rolle: "Implementierung", status: "idle", toolsCount: 11 },
  { id: "tester", name: "TESTER", hierarchie: 6, modell: "Sonnet/Opus", rolle: "Tests + Debug", status: "idle", toolsCount: 12 },
  { id: "reviewer", name: "REVIEWER", hierarchie: 5, modell: "Sonnet/Opus", rolle: "Code-Review", status: "idle", toolsCount: 11 },
  { id: "designer", name: "DESIGNER", hierarchie: 4, modell: "Sonnet/Opus", rolle: "UI/UX", status: "idle", toolsCount: 10 },
  { id: "analyst", name: "ANALYST", hierarchie: 3, modell: "Sonnet/Opus", rolle: "Repo-Analyse", status: "idle", toolsCount: 12 },
  { id: "doc-scanner", name: "DOC-SCANNER", hierarchie: 2, modell: "Haiku/Sonnet", rolle: "Web-Docs", status: "idle", toolsCount: 13 },
  { id: "devops", name: "DEVOPS", hierarchie: 2, modell: "Sonnet/Opus", rolle: "CI/CD + Deploy", status: "idle", toolsCount: 12 },
  { id: "dokumentierer", name: "DOKUMENTIERER", hierarchie: 1, modell: "Haiku/Sonnet", rolle: "Auto-Doku", status: "idle", toolsCount: 11 },
];
