# 10 — Reifegrad, echte Lücken und technischer Ausbauplan

**0.1.0 ist ein lokaler, überprüfbarer Produktionsrahmen.** Kein fertiges SaaS-Videostudio und kein unsichtbar agierender „Autofilm“-Generator. Die Produktionsphasen sind durch Dateien, Prompts, klare Regeln und manuelle Provider-Skills ausführbar; der deterministische Teil ist testbar.

## P0 — bevor man das als vollautomatische Produktion bezeichnet

- **Echte Provideradapter:** dokumentierte Higgsfield-API-Modelle versioniert integrieren, Webhook-/Polling-Logik, Cost Estimate, Idempotenz, Abbruch, Timeout, Download, Signaturprüfung und echte Sandbox-Integrationstests. Für CLI/MCP validieren, welche Toolaktionen die installierte Version bereitstellt. Nicht Provider-Requests erfinden.
- **Referenz-/Assetfreigabe:** Dateiupload, Human Approval, SHA256, Bildqualität und pro Figur/Set eindeutige Versionsnummern. Aktuell erzeugt `compile` nur vorbereitete Jobs; keine automatischen Referenzbilder.
- **Nachweisbare Nutzerfreigabe:** Zugriffsberechtigte Freigabestelle für Kosten, Rechte, gesperrte Identitäten und Release. Lokales `--confirmed` ist nur ein dokumentierter Prozessschritt.
- **Automatischer Media-Preflight:** FFprobe-Videodauer/FPS/Dimension, defekte Frames, Black Frames, Duplicate Frames, Audio-Streams vor `record`, nicht erst beim Assembly.
- **Echte QA-Bildbewertung:** framebasierte Ähnlichkeits-/Person-/Gesichtsanalyse nur im rechtlich zulässigen Kontext, Pose/Hands/Contacts, Bewegungsfluss, Flicker und Audio-/LipSync-Metriken; alle automatischen Befunde mit menschlicher Bestätigung. Ein Score aus dem LLM allein genügt nicht.
- **Ton- und NLE-Integration:** Voice-Timing, ADR, Stems, Sounddesign, LUFS/TruePeak-Analyse, J-/L-Cuts, per-Shot Trimming, Grade, Masken, Untertitelalignment und Exportprofile.
- **Recovery:** resiliente Renderqueue, sichere Retry-/Provider-Failover-Semantik, persistente Jobs, Stornierung, Crash-Recovery, Job-ID und Audit.

## P1 — Qualität und Produktivität

- Feingranulares Content-Hashing statt gesamter Episodeninvalidierung: Shot → Figuren/Set → Nachbarshots → Sound/Timeline → Release.
- 3D-Previz-Adapter für Blender, glTF/Depth/Pose/Motion mit echten Kameradaten, Kollisions- und Raumprüfung.
- Multi-Provider-Benchmark-Suite mit gleichem Testmaterial und Blindbewertung für Identität, Physik, Audio, Kosten und Nutzbarkeit.
- Sprecher- und Szenen-Continuity über Staffeln inkl. Verletzungs-/Requisiten-/Storyzustand.
- Sprechende Rollen außerhalb des Bildes / Voiceover über ausdrückliche Kennzeichnung; heutiger Validator verlangt anwesende Sprecher.
- Vollständige Episode-Writer’s-Room mit dramaturgischen Reviewrunden und automatischem Story-Dependency-Graph.
- Shot-Level Risk Planner: vorher erwartete Versuche, Kostenverteilung und Qualitätsprobleme pro Modell.
- Flexible Shot-Dauern nach Edit und automatische Lücken-/Handle-Analyse im Schnitt.

## P2 — Team-/Studio-Reife

Web-UI, gesicherte Nutzerkonten, RBAC, freigegebene Workspaces, Arbeitspakete, Freigabeoberfläche, Mehrnutzerkommentare auf Timecodes, Asset-Deduplikation, dedizierter Medien-/Objektspeicher, Versionierung/Audit, Kostenkontingente je Kunde, Observability, Wasserzeichen-/Kennzeichnungsmanagement nach geltenden Regeln, redaktionelle Rechteabnahmen, Rechnungs-/Compliance-Unterlagen, dokumentierte Datenaufbewahrung und Hosting.

## Grenzen der aktuellen FFmpeg-Assembly

Die erste Version setzt die ausgewählten Clips in Reihenfolge mit einheitlichem Format und geplanten Shotlängen zusammen. Sie mischt **nicht** automatisch die nativen Soundspuren der Clips. Kein automatisches Color Match, kein echter Mehrspur-Editor, keine Übergänge/Retiming-Gestaltung und keine Qualitätserkennung. Für einen professionellen Film müssen die Montage und der Mix zusätzlich handwerklich abgenommen werden. Ein sauberes Protokoll ist nicht dasselbe wie ein künstlerisch gelungenes Video.

## „Fertig“ bedeutet

1. Alle berücksichtigten Nutzerentscheidungen sind als versionierte Quelldateien dokumentiert.
2. Jeder ausgewählte Shot ist tatsächlich generiert, besitzt Provider-/Hash-/Kostenmetadaten und hat den 10-Punkte-Review bestanden.
3. Alle Story-, Physik-, Identitäts-, Ton-, Rechte- und Anschlussfehler wurden behoben und menschlich gesichtet.
4. Aus dem ausgewählten Material entsteht eine technisch geprüfte, emotional funktionierende und rechtlich freigabefähige Filmfassung.
5. Der Nutzer hat die finale Masterdatei, Untertitel-/Tonvarianten nach Auftrag, Produktionsnachweise und eine offene Fehlerliste (idealerweise leer).

**Nicht fertig:** „Prompts erstellt“, „Providerjob eingereicht“ oder „Video sieht in einem Standbild gut aus“.

## November 2026 Ergänzung — Cost-aware rendering

**v0.2 erledigt:** nicht-billingfähiger Kostenplan, per-Quote-Rights-/Budget-Gate, Higgscheap-Handoff und dokumentierter Higgsfield-Seedance-2.5-Draft-Final-Handoff, Draft-Frist, QA und Preisabgleich inklusive bezahlter Fehlschläge.

**Weiter offen:** Anbieter-seitig authentifizierter Live-Preis-/Status-/Rechnungsabgleich; transportgesicherte, serverseitig auditierbare, nicht manipulierbare Freigaben; tatsächliche automatische Bild-/Video-Scoring-Suite; Dreamina offizieller API-Adapter (derzeit nicht verifiziert); projektbezogene edit-list-Kostenerfassung über mehrere Episoden; Wiederaufnahme nach Prozessabsturz; feinere, shotlokale Hash-Abhängigkeiten; erneute Final-Draft-Preisverifizierung unmittelbar vor Beauftragung. Die CLI erstellt Handoffs, keine kostenpflichtigen externen Aufträge.
