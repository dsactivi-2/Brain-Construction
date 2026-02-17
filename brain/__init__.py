"""Brain System — Cloud Code Team 02.26 (DDD v3)

6-Schichten Gehirn-System fuer Multi-Agenten-Architektur.
Domain-Driven Design mit 4 Bounded Contexts + 1 Application Service.

Bounded Contexts:
  Identity       (S1) — Core Memory (Redis + JSON)
  SemanticMemory (S2) — Auto-Recall/Capture (Qdrant)
  KnowledgeGraph (S3+S5) — HippoRAG + Learning Graphs (Neo4j + Qdrant)
  Conversation   (S6) — Recall Memory (PostgreSQL + SQLite)

Application Service:
  Retrieval      (S4) — Multi-Source Router (orchestriert ueber Kontexte)

Shared Kernel:
  shared/config      — Konfiguration (databases.yaml)
  shared/connections  — DB Connection Factories
  shared/embeddings   — Vektor-Generierung (384-dim)
  shared/types        — Value Objects (Embedding, Timestamp, Score)
  shared/factory      — Composition Root (verdrahtet alle Services)
"""

__version__ = "1.0.0"
