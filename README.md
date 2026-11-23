# SHOTLOOM — Agentic Film Production System

**Von einer vagen Idee zu einer prüfbaren Filmproduktion:** Story → Serienbibel → Szenen → Shotplanung → Referenzbilder → Keyframes → Video → Schauspiel/Physik/Continuity-QA → Dialog/Foley/Musik → Schnitt → Master → Veröffentlichung.

**Stand:** 0.1.0, 23.11.2026. **Status:** lauffähiger lokaler Produktionskern, Prompt-Compiler, Stage-Gates, Kostenjournal, strukturierte menschliche Qualitätsprüfung und FFmpeg-Assembly. **Nicht enthalten:** eingebettete Videogenerierungsmodelle, automatischer Higgsfield-API-Client, KI-Drehbuch-LLM oder garantierte visuelle Qualität. Externe Generierung erfolgt über einen entsprechend angebundenen Coding-Agenten (Higgsfield CLI/Skills, MCP, ein anderer Anbieter oder lokal ComfyUI), der die Jobdateien liest und die Ergebnisse zurückregistriert.

## Warum nicht einfach „ein Prompt“?

Einzelne Video-Prompts erhalten oft keine Identität, Geografie, Timing, Materialphysik, Blicklinien und Handlung über mehrere Schnitte. SHOTLOOM macht diese Vorgaben zu einer **versionierbaren Produktionsspezifikation**. Eine andere KI übernimmt über `AGENTS.md` die Regie- und Produktionsrollen. Der Code prüft strukturelle Fehler und stoppt unfreigegebene Schritte. Ein Mensch bewertet die fertigen Bilder und den Film.

## In 10 Minuten starten

```bash
# Python 3.11+ (ffmpeg und ffprobe für die finale Montage separat installieren)
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
shotloom doctor

# Vollständige Beispielproduktion: Nachtprotokoll (6 Shots, 33 Sekunden)
shotloom validate --project projects/night-protocol
shotloom compile --project projects/night-protocol --episode EP01
shotloom preflight --project projects/night-protocol --episode EP01
shotloom next --project projects/night-protocol --episode EP01

# Eigene Filmidee als Ausgangspunkt
shotloom init --slug mein-film --title "Mein erster Film"
shotloom validate --project projects/mein-film
```

**Hinweis zum Demo-Projekt:** Die Referenzbilder und Startframes fehlen absichtlich. Die Rechtefreigabe steht absichtlich auf `false`. `preflight` muss bis zur echten Vorbereitung blockieren. Das sind keine Bugs, sondern Produktionsgates.

## Repository an deine KI übergeben

Öffne dieses Repository in Claude Code, Codex, Cursor oder einem anderen Coding-Agenten, der lokale Dateien lesen/schreiben und Befehle ausführen kann. Starte mit:

> **Lies AGENTS.md vollständig und arbeite danach als SHOTLOOM-Showrunner.** Ich beschreibe meine Filmidee frei. Erzeuge oder aktualisiere daraus `project.yaml`, `episodes/*.yaml`, Bible und Shots; respektiere alle bestehenden Freigaben und sperre Änderungen an genehmigten Identitäten, außer ich verlange sie. Arbeite schrittweise durch die Gates, fasse nur Entscheidungen mit echtem Einfluss auf Story, Rechte oder Kosten zur Freigabe zusammen. Verwende Higgsfield nur über bereits verbundene offizielle MCP-/CLI-Skills oder dokumentierte API. Generiere nichts Kostenpflichtiges ohne meine ausdrückliche Zustimmung. Prüfe jedes Ergebnis und führe Nacharbeiten nur an betroffenen Shots durch. Liefere erst nach menschlicher Finalabnahme einen Master und einen klaren Bericht über offene Mängel.

Für einen vollständig kopierbaren Einstieg siehe **[START_HERE_PROMPT.md](START_HERE_PROMPT.md)**.

Zusätzliche fachliche Rollen liegen in `agents/`, ausführbare Arbeitsanweisungen in `skills/`, filmisches Handwerk in `docs/`.

## Tatsächlicher Produktionsablauf

| Gate | Wer | Nachweis | Stop-Regel |
|---|---|---|---|
| G0 Brief | Showrunner + Nutzer | Projektidee, Ziel, Publikum, Länge, Budget | keine erfundene Einwilligung |
| G1 Story | Autor + Dramaturg | Logline, Konflikt, Beat Sheet, Skript | keine ungeklärten Story-Widersprüche |
| G2 Bible | Casting, Ausstattung | Identität, Kostüm, Stimme, Ort, Requisiten | keine wechselnden Identitäten |
| G3 Coverage | Regie + Kamera | Szenenräume, Achse, Shots, Timing, Sound-Cues | alle Szenen und Dialoge abgedeckt |
| G4 References | Visual Director | freigegebene Personen-/Setreferenzen + Start-/Endframes | i2v nicht ohne Startframe |
| G5 Preflight | Production Manager | `validate`, `preflight`, Kosten/Zustimmung | kein bezahlter Render ohne Freigabe |
| G6 Generate | Agent mit Provider | ein Job pro Shot, Originaldatei + Provenienz | keine stillen Modellwechsel |
| G7 Quality | Menschen + Kritiker-Agent | 10 Kriterien, Fehler/Neuanlauf | kein Auswahlstatus bei Fehler |
| G8 Post | Schnitt + Sound | Schnitt, Sprachfassung, Foley, Musik, Mix | kein Dialogfilm ohne geprüften Ton |
| G9 Release | Nutzer | voller Durchlauf, Master-Hash, Rechte, Deliverables | `release` nur nach Abnahme |

**Quellpriorität:** jüngste ausdrückliche Nutzerentscheidung > genehmigte Projekt-Bible > Episodenspezifikation > Shotbrief > Generatorvorschlag. Nie einen Fix durch Veränderung der festen Figur oder der Raumlogik „erkaufen“.

## Konkrete CLI nach dem ersten Render

```bash
# Erst nach tatsächlichem Rechtecheck: in project.yaml policy.rights_cleared=true;
# echte Referenzdateien und Startframes hinterlegen; erneut compile + preflight.
# Danach mit ausdrücklich erteilter, konkreter Nutzerzustimmung:
shotloom authorize --project projects/mein-film --episode EP01 --shot EP01-S001 \
  --max-cost 2.50 --by "Freigeber" --confirmed

# Der verbundene KI-Agent generiert nur diesen Job und speichert den Clip lokal.
shotloom record --project projects/mein-film --episode EP01 --shot EP01-S001 \
  --file /pfad/zum/ergebnis.mp4 --provider higgsfield-cli --model "gewähltes-modell" --cost 1.20

# Menschlicher Review: jedes der 10 Kriterien von 0 bis 5 bewerten
shotloom review --project projects/mein-film --episode EP01 --shot EP01-S001 \
  --attempt 1 --reviewer "Filmreview" \
  --score identity=5 --score continuity=5 --score anatomy_physics=4 \
  --score performance=5 --score cinematography=5 --score light=4 \
  --score editability=5 --score sound_sync=4 --score artifact_free=5 --score storytelling=4
shotloom select --project projects/mein-film --episode EP01 --shot EP01-S001 --attempt 1

# Nach Auswahl ALLER Shots: Finalmix als separate Datei bereitstellen.
shotloom assemble --project projects/mein-film --episode EP01 --audio-master /pfad/mix.wav
shotloom subtitles --project projects/mein-film --episode EP01  # nur Rohentwurf, Timing korrigieren
shotloom release --project projects/mein-film --episode EP01 \
  --master projects/mein-film/output/EP01_master.mp4 --by "Filmabnahme" --confirmed
```

Ein bereits genehmigter Clip wird beim Wechsel zentraler Projekt- oder Episodenfakten wegen einer neuen **Kreativvertrag-Prüfsumme** ungültig und kann nicht mehr unverändert montiert werden. Das verhindert die häufige Falle „Drehbuch geändert, alter Shot bleibt fälschlich freigegeben“; derzeit wird konservativ die ganze Episode invalidiert. Eine feinere Abhängigkeitsanalyse ist in `docs/10_roadmap.md` vorgesehen.

## Higgsfield und Alternativen

- **Coding-Agenten:** offizieller Higgsfield CLI/Skills-Weg (`npx skills add higgsfield-ai/skills`, dann `higgsfield auth login`; aktuelle Skill-Quelle `https://github.com/higgsfield-ai/skills`); der Agent erhält `compiled/<episode>/jobs/*.json` und `prompts/*.md`.
- **MCP-Agenten:** offizieller MCP-Endpunkt `https://mcp.higgsfield.ai/mcp`, Verbindung über OAuth.
- **Eigene Software/API:** separate Higgsfield-API mit eigenem Guthaben und modellabhängiger REST-Spezifikation. Eine API-Integration ist bewusst nicht simuliert; sie muss gegen die jeweils aktuelle offizielle Dokumentation implementiert und getestet werden.
- **Ohne Higgsfield:** gleiche Jobdateien als Arbeitsauftrag an ComfyUI oder andere Provider übergeben. Unterschiede der Fähigkeiten vor jedem Run prüfen.

**Abrechnung:** Higgsfield-MCP/CLI verwendet laut offizieller Dokumentation Plan-Credits; die API ein gesondertes USD-Guthaben. Unbegrenzte Website-Modelle bedeuten **nicht**, dass automatisierte Generation kostenlos ist. Siehe `docs/06_integrations.md`.

## Sicherheit, Qualität und Grenzen

Die CLI erzeugt **niemals eigenständig kostenpflichtige API-Aufrufe**. `--confirmed` bildet nur eine dokumentierte Zustimmung ab und ist kein beweissicheres Signaturverfahren. Ein Agent könnte lokale Daten technisch editieren; bei produktiver Mehrbenutzer-Nutzung sind serverseitige Berechtigungen erforderlich. Medien bleiben lokal, Git ignoriert große Renderdateien. Keine Key-Dateien committen. Rechts- und Einwilligungslage ist vor jeder öffentlichen Nutzung individuell zu prüfen.

FFmpeg kann Clips zusammenfügen, aber garantiert weder echtes Acting noch korrektes Physikverhalten, noch einen guten Schnitt. Ein Interpolator macht aus einer anatomisch unmöglichen Szene keine richtige Physik. Im Review zählen Originalframes, volle Geschwindigkeit, Ton und Übergänge – nicht nur hübsche Standbilder.

## Struktur

```text
AGENTS.md               verbindliches Regelwerk für alle Coding-Agenten
CLAUDE.md               Claude-Startpunkt
agents/                 spezialisierte Regie-, Continuity-, Kamera-, Physik-, Audio-Rollen
skills/*/SKILL.md       stufenweise, providerneutrale Arbeitsaufträge
shotloom/               CLI, JSON Schema Validator, Compiler, State, QA, Assembly
schemas/                maschinenlesbare Projekt- und Episodenverträge
templates/              neues Projekt und erste Episode
projects/night-protocol/  fertiges 33-s-Demodrehbuch, aber ohne fehlende echte Medien
docs/                   tiefes Filmhandwerk und Providerintegration
.github/workflows/ci.yml automatisierte Struktur- und Unit-Tests
tests/                  Tests der Workflowregeln
```

Dieses Repo ist ein **eigenständiger Arbeitsrahmen**, keine Kopie fremder GitHub-Projekte. Externe Ansätze, Quellen und Lizenzhinweise sind in `docs/09_research_sources.md` nachvollziehbar dokumentiert. Eigene Softwarelizenz: MIT; das sagt nichts über die Rechte an eingebundenen Modellen, Assets, Stimmen, Musik oder Videogenerierungen aus.
