---
name: shotloom-render-handoff
description: Invoke only the actual connected provider workflow and record one output per attempt.
---

# Video generieren / Provider-Handoff

**Aktivierung:** Wenn die Projektphase oder der Nutzerwunsch zu dieser Aufgabe gehört. Bearbeite nur Zuständigkeiten dieser Skill; für andere Phasen an Showrunner delegieren. Lies `AGENTS.md` und die relevante `docs/*.md`-Anleitung.

## Ablauf

Führe `validate`, `compile`, `preflight` aus. Nach echter Nutzerfreigabe `authorize` verwenden. Lies job.json und prompt.md, sammele tatsächlich existierende Referenzdateien, prüfe Providerlimits. Generiere mit offizieller CLI/MCP/API-Fähigkeit, warte auf echten Abschluss und lade Medien herunter. `record` speichert lokalen Versuch mit Kosten/Hash. Bei Fehler keine Fake-Completion und keine zweite kostenpflichtige Bestellung ohne erneute Freigabe.

## Verbindliche Artefakte

realer Clip, record-Metadaten, Ausgabedatei

## Abnahmekriterium

G6: decodierbares Originalfile, beobachtbare Provenienz, keine Budgetverletzung.

## Stop und Übergabe

Bei fehlenden Rechten, nicht vorhandenen Providerfähigkeiten, Mehrkosten ohne Freigabe oder Konflikt mit genehmigter Bible: stoppen und konkrete Fakten statt Spekulation liefern. Gib IDs, echte Dateinamen, Tests, offene Blocker und die nächste Aktion an.
