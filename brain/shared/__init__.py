"""Shared Kernel — Brain System DDD v3

Gemeinsame Infrastruktur fuer alle Bounded Contexts:
- config: Konfiguration laden (databases.yaml)
- connections: DB Connection Factories (Qdrant, Neo4j, Redis, PostgreSQL, SQLite)
- embeddings: Vektor-Generierung (sentence-transformers)
- types: Value Objects (Embedding, Timestamp, Score)
- factory: Composition Root (verdrahtet alle Services)
"""
