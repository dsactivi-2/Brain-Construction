import { NextResponse } from "next/server";
import { Task } from "@/lib/types";

// In-memory task store (in production: Redis or PostgreSQL)
let tasks: Task[] = [
  {
    id: "task-1",
    title: "PPR + spaCy NER Upgrade",
    description: "S3 Knowledge Graph: Echten PageRank statt connection/10, spaCy Entity Extraction statt Regex",
    assignedAgent: "coder",
    priority: 9,
    status: "done",
    createdAt: "2026-02-17T10:00:00Z",
    updatedAt: "2026-02-17T14:30:00Z",
  },
  {
    id: "task-2",
    title: "v3.0 Agent Profile JSON Export",
    description: "Alle 11 Agent-Profile als JSON exportieren, Grundprofil mergen",
    assignedAgent: "architekt",
    priority: 8,
    status: "done",
    createdAt: "2026-02-17T15:00:00Z",
    updatedAt: "2026-02-17T22:30:00Z",
  },
  {
    id: "task-3",
    title: "17 Hooks implementieren",
    description: "SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, Stop, SessionEnd, etc.",
    assignedAgent: "coder",
    priority: 8,
    status: "backlog",
    createdAt: "2026-02-18T00:00:00Z",
    updatedAt: "2026-02-18T00:00:00Z",
  },
  {
    id: "task-4",
    title: "Brain-System Tests schreiben",
    description: "Unit Tests fuer alle 6 Schichten, Integration Tests fuer Brain-Tools",
    assignedAgent: "tester",
    priority: 7,
    status: "backlog",
    createdAt: "2026-02-18T00:00:00Z",
    updatedAt: "2026-02-18T00:00:00Z",
  },
  {
    id: "task-5",
    title: "Docker Deployment verifizieren",
    description: "Health-Checks aller 8 Services, Smoke Tests, Performance Baseline",
    assignedAgent: "devops",
    priority: 7,
    status: "in_progress",
    createdAt: "2026-02-18T00:00:00Z",
    updatedAt: "2026-02-18T00:30:00Z",
  },
  {
    id: "task-6",
    title: "Kanban Dashboard bauen",
    description: "Next.js Full-Stack Dashboard mit Agent-Monitor, Health, Event-Bus",
    assignedAgent: "designer",
    priority: 6,
    status: "in_progress",
    createdAt: "2026-02-18T00:00:00Z",
    updatedAt: "2026-02-18T01:00:00Z",
  },
];

export async function GET() {
  return NextResponse.json(tasks);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newTask: Task = {
    id: `task-${Date.now()}`,
    title: body.title,
    description: body.description || "",
    assignedAgent: body.assignedAgent,
    priority: body.priority || 5,
    status: body.status || "backlog",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  tasks.push(newTask);
  return NextResponse.json(newTask, { status: 201 });
}

export async function PUT(request: Request) {
  const body = await request.json();
  const idx = tasks.findIndex((t) => t.id === body.id);
  if (idx === -1) return NextResponse.json({ error: "Not found" }, { status: 404 });
  tasks[idx] = { ...tasks[idx], ...body, updatedAt: new Date().toISOString() };
  return NextResponse.json(tasks[idx]);
}

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const id = searchParams.get("id");
  tasks = tasks.filter((t) => t.id !== id);
  return NextResponse.json({ ok: true });
}
