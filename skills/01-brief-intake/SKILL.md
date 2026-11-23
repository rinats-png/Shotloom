---
name: shotloom-brief-intake
description: Turn a free-form film idea and user additions into a production project without losing intent.
---

# Brief und Projektstart

**Aktivierung:** Wenn die Projektphase oder der Nutzerwunsch zu dieser Aufgabe gehört. Bearbeite nur Zuständigkeiten dieser Skill; für andere Phasen an Showrunner delegieren. Lies `AGENTS.md` und die relevante `docs/*.md`-Anleitung.

## Ablauf

Übertrage Nutzeridee in Logline, Zielpublikum, Format, Laufzeit, Sprache, Vertriebsziel und Budget. Markiere fehlende ästhetische Details als Annahmen. Trenne harte Grenzen von editierbaren Vorschlägen. Erzeuge mit `shotloom init --slug ... --title ...` eine gültige Vorlage; editiere `project.yaml`; prüfe `validate`. Nur essentielle Einwilligungs-/Budgetdetails zum Gate blockieren, keine langen Pflichtfragebögen.

## Verbindliche Artefakte

project.yaml, notes.md

## Abnahmekriterium

G0 mit Nutzerauftrag dokumentiert, Budget standardmäßig 0 und Rechte standardmäßig nicht freigegeben.

## Stop und Übergabe

Bei fehlenden Rechten, nicht vorhandenen Providerfähigkeiten, Mehrkosten ohne Freigabe oder Konflikt mit genehmigter Bible: stoppen und konkrete Fakten statt Spekulation liefern. Gib IDs, echte Dateinamen, Tests, offene Blocker und die nächste Aktion an.
