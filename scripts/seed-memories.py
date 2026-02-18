#!/usr/bin/env python3
"""Seed-Script — Laedt initiale Memories in S2 (Qdrant).

Wird einmalig beim ersten Setup ausgefuehrt.
Prueft auf Duplikate (Score > 0.95 = bereits vorhanden).
"""

import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_DIR)

SEED_MEMORIES = [
    {
        "text": "Verfuegbare Templates in amp-brain/templates/: 01-change-request-template.md, 02-impact-assessment-matrix-template.md, 03-phase-revalidation-checklist-template.md, 04-bug-report-template.md, 05-daily-standup-template.md, 06-weekly-report-template.md, EXAMPLE-PROJECT-README.md",
        "scope": "projekt",
        "type": "fakt",
        "priority": 5,
    },
    {
        "text": "Projekt-spezifische Anweisungen: CRM Projekte (crm, CRM-activi) folgen ~/activi-dev-repos/amp-brain/FOLGE_CRM.md. Cloud Code Projekte (code-cloud-agents) folgen ~/activi-dev-repos/amp-brain/FOLGE_ACTIVI_CLOUD_CODE.md",
        "scope": "projekt",
        "type": "fakt",
        "priority": 6,
    },
]


def main():
    try:
        from brain.shared.factory import get_semantic_memory_service
        svc = get_semantic_memory_service()
    except Exception as e:
        print(f"[FEHLER] Brain-Service nicht verfuegbar: {e}")
        print("         Stelle sicher dass Qdrant laeuft (docker compose up -d)")
        sys.exit(1)

    stored = 0
    skipped = 0

    for mem in SEED_MEMORIES:
        try:
            result = svc.store(**mem)
            if result.get("stored"):
                stored += 1
                print(f"  [OK] Gespeichert: {mem['text'][:60]}...")
            else:
                skipped += 1
                reason = result.get("reason", "duplikat")
                print(f"  [SKIP] {reason}: {mem['text'][:60]}...")
        except Exception as e:
            print(f"  [FEHLER] {e}: {mem['text'][:60]}...")

    print(f"\nFertig: {stored} gespeichert, {skipped} uebersprungen")


if __name__ == "__main__":
    print("=== Brain S2 Seed: Initiale Memories laden ===\n")
    main()
