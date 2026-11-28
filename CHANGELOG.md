# Changelog

## 0.2.0 — 2026-11-28

- Szenenkomplexität und kostenorientiertes Draft-/Final-Routing; nicht live bindende Planung (`cost-plan`).
- Provider-gebundene Einmal-Quoten, 30-Minuten-Preisquote-TTL, Freigaben inkl. offener Budgetreservierungen.
- Kostenfreier Request-Handoff für Higgscheap und dokumentierte offizielle Higgsfield-Seedance-2.5-Draft/Finalize-API, ohne ungetestete autonome Provideraufrufe.
- Vermeidung nicht freigegebener Finalshots: Preview-only-Verbot, menschliche QA, Hash-Driftprüfung, selbe Konto-ID, Sieben-Tage-Frist und kürzeres Ablaufdatum.
- Fehlgeschlagene kostenpflichtige Versuche verbuchbar, definitiv unversendete Reservierungen stornierbar.
- Dreamina-Kosten- und Verfügbarkeitsnotiz mit Preis-/Promotionstrennung; kein fingierter API-Adapter.
- Zusätzliche Anleitungen, Agent, Skill, Vorlagen und Tests (18 lokale Tests zum Releasezeitpunkt).

## 0.1.0 — 2026-11-23

- Erstes eigens entwickeltes SHOTLOOM-Repository: 10-Gate Filmproduktion, Agentenvertrag, 15 spezialisierte Agenten und 15 Skills.
- Projekt-/Episode-JSON-Schemas, YAML-Vorlagen, eigenständiger Prompt-Compiler und providerneutrales Generation-Handoff.
- Structural-/Continuity-Validator, Rechte-/Referenz-/Kosten-Preflight, per-Versuch-Freigabe und Kostenjournal.
- FFprobe-Mediendatei-Prüfung, menschliche 10-Kriterien-Review, selektierbare Versuche, SHA256-Bindung an Kreativvertrag.
- FFmpeg-Rohmontage, Untertitel-Entwurf und menschliches Releaseprotokoll.
- Vollständiges Demo-Drehbuch für eine 33-s-Episode mit sechs detaillierten Shots (ohne erfundene Mediengenerierung).
- Dokumentation zu Identität, Schauspiel, Physik, Kamera, Ton, Rights, Higgsfield CLI/MCP/API, ComfyUI und Quellen.

**Nicht enthalten:** echter Render-API-Adapter, Bild-/Video-KI im Repository, automatisierte Kunst-/Audio-QA, professioneller NLE, serverseitige Signatur von Nutzerfreigaben. Siehe `docs/10_roadmap.md`.
