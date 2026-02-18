"use client";

import { useState, useEffect, useCallback } from "react";
import { Task, KANBAN_COLUMNS, KanbanColumn, AGENTS } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import { Plus, GripVertical } from "lucide-react";

export default function KanbanBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [draggedTask, setDraggedTask] = useState<string | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const fetchTasks = useCallback(async () => {
    const res = await fetch("/api/tasks");
    const data = await res.json();
    setTasks(data);
  }, []);

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 10000);
    return () => clearInterval(interval);
  }, [fetchTasks]);

  const moveTask = async (taskId: string, newStatus: KanbanColumn) => {
    await fetch("/api/tasks", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: taskId, status: newStatus }),
    });
    fetchTasks();
  };

  const addTask = async (title: string, description: string, assignedAgent: string, priority: number) => {
    await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description, assignedAgent, priority }),
    });
    setShowAddModal(false);
    fetchTasks();
  };

  const priorityColor = (p: number) => {
    if (p >= 9) return "text-red-400 bg-red-500/10";
    if (p >= 7) return "text-amber-400 bg-amber-500/10";
    if (p >= 5) return "text-blue-400 bg-blue-500/10";
    return "text-slate-400 bg-slate-500/10";
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold">Kanban Board</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
        >
          <Plus size={16} /> Neuer Task
        </button>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {KANBAN_COLUMNS.map((col) => (
          <div
            key={col.id}
            className="bg-slate-800/50 rounded-xl p-3 min-h-[400px]"
            onDragOver={(e) => e.preventDefault()}
            onDrop={() => {
              if (draggedTask) {
                moveTask(draggedTask, col.id);
                setDraggedTask(null);
              }
            }}
          >
            <div className="flex items-center gap-2 mb-4">
              <div className={`w-3 h-3 rounded-full ${col.color}`} />
              <h3 className="font-semibold text-sm">{col.title}</h3>
              <span className="ml-auto text-xs text-slate-500 bg-slate-700 px-2 py-0.5 rounded-full">
                {tasks.filter((t) => t.status === col.id).length}
              </span>
            </div>

            <div className="space-y-2">
              {tasks
                .filter((t) => t.status === col.id)
                .sort((a, b) => b.priority - a.priority)
                .map((task) => (
                  <div
                    key={task.id}
                    draggable
                    onDragStart={() => setDraggedTask(task.id)}
                    className="bg-slate-800 rounded-lg p-3 cursor-grab active:cursor-grabbing border border-slate-700 hover:border-slate-600 transition-colors"
                  >
                    <div className="flex items-start gap-2">
                      <GripVertical size={14} className="text-slate-600 mt-0.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{task.title}</p>
                        <p className="text-xs text-slate-400 mt-1 line-clamp-2">
                          {task.description}
                        </p>
                        <div className="flex items-center gap-2 mt-2">
                          <span className={`text-xs px-1.5 py-0.5 rounded ${priorityColor(task.priority)}`}>
                            P{task.priority}
                          </span>
                          {task.assignedAgent && (
                            <span className="text-xs text-slate-400">
                              @{task.assignedAgent}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        ))}
      </div>

      {/* Add Task Modal */}
      {showAddModal && (
        <AddTaskModal
          onClose={() => setShowAddModal(false)}
          onAdd={addTask}
        />
      )}
    </div>
  );
}

function AddTaskModal({
  onClose,
  onAdd,
}: {
  onClose: () => void;
  onAdd: (title: string, desc: string, agent: string, priority: number) => void;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [agent, setAgent] = useState("berater");
  const [priority, setPriority] = useState(5);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl p-6 w-full max-w-md border border-slate-700">
        <h3 className="text-lg font-bold mb-4">Neuer Task</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-slate-400 block mb-1">Titel</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Task-Titel..."
            />
          </div>
          <div>
            <label className="text-xs text-slate-400 block mb-1">Beschreibung</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 h-20"
              placeholder="Beschreibung..."
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">Agent</label>
              <select
                value={agent}
                onChange={(e) => setAgent(e.target.value)}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {AGENTS.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name} (H{a.hierarchie})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">Priority (1-10)</label>
              <input
                type="number"
                min={1}
                max={10}
                value={priority}
                onChange={(e) => setPriority(Number(e.target.value))}
                className="w-full bg-slate-700 border border-slate-600 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors"
          >
            Abbrechen
          </button>
          <button
            onClick={() => title && onAdd(title, description, agent, priority)}
            disabled={!title}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white rounded-lg text-sm transition-colors"
          >
            Erstellen
          </button>
        </div>
      </div>
    </div>
  );
}
