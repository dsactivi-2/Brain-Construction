// === API helpers to connect to Docker services ===

const SERVICES = {
  ragApi: "http://localhost:8100",
  docScanner: "http://localhost:8101",
  hipporag: "http://localhost:8102",
  neo4j: "http://localhost:7474",
  qdrant: "http://localhost:6333",
};

export async function fetchServiceHealth(
  name: string,
  url: string
): Promise<{ status: string; responseTime: number; details?: Record<string, string> }> {
  const start = Date.now();
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(5000), cache: "no-store" });
    const responseTime = Date.now() - start;
    if (!res.ok) return { status: "degraded", responseTime };
    const data = await res.json();
    return { status: "healthy", responseTime, details: data };
  } catch {
    return { status: "down", responseTime: Date.now() - start };
  }
}

export async function fetchAllHealth() {
  const [ragApi, docScanner, hipporag, qdrant] = await Promise.all([
    fetchServiceHealth("rag-api", `${SERVICES.ragApi}/health`),
    fetchServiceHealth("doc-scanner", `${SERVICES.docScanner}/health`),
    fetchServiceHealth("hipporag", `${SERVICES.hipporag}/health`),
    fetchServiceHealth("qdrant", `${SERVICES.qdrant}/collections`),
  ]);
  return { ragApi, docScanner, hipporag, qdrant };
}

export async function fetchQdrantStats() {
  try {
    const res = await fetch(`${SERVICES.qdrant}/collections`, { cache: "no-store" });
    const data = await res.json();
    const collections = data.result?.collections || [];
    return { collections: collections.length, names: collections.map((c: { name: string }) => c.name) };
  } catch {
    return { collections: 0, names: [] };
  }
}

export async function fetchNeo4jStats() {
  try {
    // Neo4j requires auth, so we just check if it's reachable
    const res = await fetch(SERVICES.neo4j, { cache: "no-store" });
    if (res.ok) {
      const data = await res.json();
      return { version: data.neo4j_version || "unknown", status: "connected" };
    }
    return { version: "unknown", status: "error" };
  } catch {
    return { version: "unknown", status: "down" };
  }
}
