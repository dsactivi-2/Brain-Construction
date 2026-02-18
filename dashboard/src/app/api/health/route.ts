import { NextResponse } from "next/server";

const SERVICES = [
  { name: "rag-api", url: "http://localhost:8100/health", port: 8100, schicht: "S4" },
  { name: "doc-scanner", url: "http://localhost:8101/health", port: 8101, schicht: "-" },
  { name: "hipporag", url: "http://localhost:8102/health", port: 8102, schicht: "S3" },
  { name: "neo4j", url: "http://localhost:7474", port: 7474, schicht: "S3+S5" },
  { name: "qdrant", url: "http://localhost:6333/collections", port: 6333, schicht: "S2+S3" },
  { name: "redis", url: null, port: 6379, schicht: "S1" },
  { name: "recall-db", url: null, port: 5432, schicht: "S6" },
];

async function checkService(svc: typeof SERVICES[0]) {
  if (!svc.url) {
    return { ...svc, status: "unknown", responseTime: 0, details: {} };
  }
  const start = Date.now();
  try {
    const res = await fetch(svc.url, { signal: AbortSignal.timeout(5000), cache: "no-store" });
    const responseTime = Date.now() - start;
    let details = {};
    try { details = await res.json(); } catch { /* not JSON */ }
    return { ...svc, status: res.ok ? "healthy" : "degraded", responseTime, details };
  } catch {
    return { ...svc, status: "down", responseTime: Date.now() - start, details: {} };
  }
}

export async function GET() {
  const results = await Promise.all(SERVICES.map(checkService));
  return NextResponse.json(results);
}
