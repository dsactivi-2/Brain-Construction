"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Columns3,
  HeartPulse,
  Users,
  Brain,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/kanban", label: "Kanban", icon: Columns3 },
  { href: "/health", label: "Health", icon: HeartPulse },
  { href: "/agents", label: "Agents", icon: Users },
  { href: "/memory", label: "Memory", icon: Brain },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-slate-900 text-white flex flex-col min-h-screen">
      <div className="p-4 border-b border-slate-700">
        <h1 className="text-lg font-bold">Brain System</h1>
        <p className="text-xs text-slate-400">Cloud Code Team 02.26</p>
      </div>
      <nav className="flex-1 p-2">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm mb-1 transition-colors ${
                active
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-700 text-xs text-slate-500">
        v3.0 &middot; 11 Agents &middot; 6 Layers
      </div>
    </aside>
  );
}
