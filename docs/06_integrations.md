# 06 — Higgsfield, andere Modelle und Providerwechsel (Stand November 2026)

## Der zentrale Architekturentscheid

SHOTLOOM **generiert den providerneutralen Shot-Job**, nicht von sich aus ein Video. Das JSON aus `compiled/EPxx/jobs/EPxx-Sxxx.json` ist eine **Arbeitsanweisung an einen Agenten**, kein angeblicher Higgsfield-Request. Der verbundene Agent ermittelt die zur Laufzeit real verfügbaren Tools/Modelle und deren Ein- und Ausgabeschranken, zahlt höchstens nach genehmigtem Kostenbudget und lädt das Ergebnis herunter. Diese Trennung verhindert Schein-Integrationen und erzwungene Anbieterbindung.

## Higgsfield: drei **verschiedene** Wege

### A — Coding-Agent (empfohlen für Claude Code/Cursor/Codex)

Offizielle Dokumentation: https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-access-higgsfield-via-cli
Aktuelle Skill-Quelle: https://github.com/higgsfield-ai/skills (MIT-Lizenz laut GitHub-Ansicht, nicht im Repo kopiert)

```
npx skills add higgsfield-ai/skills
higgsfield auth login
```

Danach kann ein unterstützter Coding-Agent gemäß offizieller Anleitung `/higgsfield:higgsfield-generate` oder die dort installierte Skill verwenden. Der Agent muss die **tatsächlich installierten Namen und Parameter** aus den Tools lesen. Keine unbestätigten Flags erfinden. Installieren und Account autorisieren muss der Kontoinhaber. Für Animation: zuerst Frames und Referenzen prüfen; dann komplette Shot-Anweisung + vorhandene Assets senden; Ergebnis samt Provider und Modell erfassen.

### B — MCP (für unterstützte Chat- oder Entwickler-Agenten)

Offizieller MCP-Endpunkt: `https://mcp.higgsfield.ai/mcp`.
Quelle: https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp

Nutzt OAuth und Plan-Credits. Ein MCP-Agent erhält Tool-Definitionen über seine Verbindung, **nicht** aus diesem Repo. Toolparameter, Preis, Auflösung, Referenzbilder, Start-/Endframe-Support und erlaubte Dauer pro Aufruf prüfen. Higgsfield dokumentiert unter anderem Character-/Soul-, Bild-, Video- und Audiofunktionen. Das Vorhandensein einer Funktion auf der Website garantiert nicht ihre Verfügbarkeit in jeder Modellkonfiguration.

### C — Separate Developer API

Offizielle Docs: https://docs.higgsfield.ai/docs
Offizieller Überblick: https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api

API-Abrechnung in USD von separatem Guthaben (nicht Website-Plan-Credits); asynchrone Jobs mit Request-ID, Status oder Webhook; laut Dokumentation Ergebnisse nur begrenzt auf dem Dienst gespeichert, also zügig herunterladen. Modellabhängige Payload und Kostenschätzung sind aus der **jeweils aktuellen Modellseite** zu beziehen. Nie sensible API-Key-Teile in Repository, Logs oder Prompt schreiben. **Der aktuelle SHOTLOOM-Kern enthält aus gutem Grund noch keinen Higgsfield-API-Client.** Für eine produktive Clientimplementierung fehlen in diesem Prototyp verifizierte modellkonkrete Requests, Fehler-/Retry-Semantik, signaturgeprüfte Webhooks, Medienvalidierung und Integrationstests mit tatsächlichem Konto.

**Wichtig:** Unlimited-Website-Tarife gelten nicht automatisch für MCP/CLI/API. Die offiziellen Quellen sagen für MCP/CLI Credits, für die API USD-Guthaben. Alle Kosten pro Render zählen auch bei einem durch den Agenten ausgelösten Test.

## Modellwahl anhand Fähigkeiten (nicht Marketing)

Erfasse vor dem Render in einem Modellsteckbrief:

| Fähigkeit | Zu prüfen |
|---|---|
| Text-to-Video / Image-to-Video | wirklich verfügbar, mit passendem Input |
| Referenzsteuerung | Zahl, Bildtypen, Kompression, Uploadlimits |
| Start-/Endframe | beide steuerbar oder nur initiale Bildkonditionierung |
| Video-to-Video / Motion Transfer | geeignet für komplizierte Body-/Kamera-Choreografie |
| Identitätsanker/Soul | Training, Nutzungsrechte, Provenienz |
| Audiogenerierung | Dialog/SFX/Voice oder nur Stummvideo; Sprachunterstützung |
| Kliplänge / FPS / Auflösung | echtes Ergebnis und gewünschte Ausgabe; nicht nur Upscaling |
| Temporalität | stabiler Charakter, Schatten, Hand-Objekt-Kontakt, Blicklinien |
| Kosten / Wartezeit / Queue | Preis pro Versuch, Fehlversuch, Status, Downloadfrist |
| kommerzielle Nutzung | vertraglich für konkretes Modell/Tarif erlaubt |

Start mit einem günstigen Pilot-Shot; derselbe Modellname kann über Zeit andere Versionen und Tarife meinen. Modellwechsel nur mit protokollierter Review-Entscheidung. Bei gleich guten Ergebnissen Provider nach Kosten, Referenzqualität, Steuerbarkeit und Rechtslage wählen.

## Lokale/Open-Source-Alternative

https://github.com/Comfy-Org/ComfyUI bietet Graphen/Workflows für verschiedene Bild-/Video-/Audio-Modelle. Dort lassen sich z. B. Wan- und LTX-Familien einsetzen, sofern Modell und passende Hardware/Nodes vorhanden sind. Ein konkreter Workflow muss mit seiner eigenen Modellversion getestet und versioniert werden. ComfyUI selbst bedeutet weder „kostenloser Strom“ noch ein kostenloses Cloud-Modell. GPU/VRAM/Speicher, Lizenz und Queue-Verhalten prüfen. Der Kern von SHOTLOOM legt nur den Vertrag fest; Workflow-JSONs sind **nicht** vorgetäuscht.

## Operator-Ablauf für einen Job

1. Aktuelle `shotloom validate`- und `preflight`-Ergebnisse lesen; alle Blocker beheben.
2. Modellsteckbrief und Kostenschätzung beim echten Anbieter abrufen. Referenzzahl und Startframe-Modus gegen Capability-Tabelle prüfen.
3. Nutzer um Freigabe des **konkreten** Shots + max. Kostenbetrag bitten; `authorize` nur nach echtem Ja.
4. Job + Prompt + Referenzen über die **verbundene** Provider-Skill/MCP-Konfiguration generieren.
5. Output herunterladen und mindestens als decodierbare Videodatei prüfen. Nicht als abgeschlossen markieren, wenn nur eine URL oder ein Request-ID existiert.
6. `record` mit tatsächlichen Kosten und Provider/Modell, danach Frame-Review, `review` und `select`.
7. Nach Fehlversuchen Budget und Plan neu prüfen; kein unlimitierter Retry-Loop.

## Adaptervertrag (für Entwickler)

Input: `job.json`, `prompt.md`, freigegebene Referenzdateien, bewusstes Nutzer-Approval, kostengeprüfter Provider/Modell-Snapshot.

Output: `request_id`, tatsächlich gewählte Modellversion, Jobstatus, Outputdatei lokal, Metadaten (FPS/Dauer/Auflösung/Audio), Rechnungsbetrag, Fehlercode und Download-/Lizenznachweise. Keine Secretwerte in Ergebnisdateien. Ein `submit()` darf nur mit Autorisierung und limitierter Retry-Zahl handeln; Polling darf keine neue kostenpflichtige Erzeugung auslösen; Download muss vor Ablauf der Host-Dateifrist stattfinden.

**Ein Modell mit nativem Ton ersetzt nicht automatisch Sounddesigner, Dialogediting oder Finalmix.**
