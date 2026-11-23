# 09 — Recherchequellen / Einordnung (23.11.2026)

Die folgenden Quellen waren bei Erstellung öffentlich auffindbar. Im Repo wurden ihre **Methoden analysiert und in ein eigenständiges System übersetzt**, kein fremder Quellcode ungeprüft übernommen. Lizenz, Versionsstand und tatsächliche Implementierung bitte vor Wiederverwendung erneut prüfen; README-Behauptungen sind keine unabhängigen Benchmarks.

## Offizielle Primärquellen

- **Higgsfield-Skill-Repository:** https://github.com/higgsfield-ai/skills — offizielle Skills (aktuell u. a. `higgsfield-generate` und `higgsfield-soul-id`), MIT-Lizenz laut GitHub-Ansicht. Keine fremden Dateien eingebettet.
- **Higgsfield CLI/Skills:** https://higgsfield.ai/creator-hub/help-center/integrations/how-do-i-access-higgsfield-via-cli — offizieller Coding-Agent-Zugang, `npx skills add higgsfield-ai/skills`, OAuth CLI.
- **Higgsfield MCP:** https://higgsfield.ai/creator-hub/help-center/integrations/what-is-higgsfield-mcp — offizieller MCP-Endpunkt und Credit-Verhalten.
- **Higgsfield API:** https://higgsfield.ai/creator-hub/help-center/integrations/what-is-the-higgsfield-api und https://docs.higgsfield.ai/docs — separate Guthabenabrechnung, asynchroner API-Workflow, Referenz für echte Integration.
- **ComfyUI:** https://github.com/Comfy-Org/ComfyUI — ausführbare graphbasierte Workflows und lokale Modellanbindung; eigene GPL-3.0-Lizenz beachten, Code hier nicht eingebettet.
- **Comfy CLI:** https://github.com/Comfy-Org/comfy-cli — offizielle lokale/Cloud-Kommandozeile für ComfyUI, GPL-3.0; für spätere Adapter interessant.
- **PySceneDetect:** https://github.com/Breakthrough/PySceneDetect — Szenen-/Schnitterkennung und praktische visuelle Analyse; BSD-3-Clause. Nicht als Identitätsprüfer ausgeben.
- **FFmpeg:** https://ffmpeg.org/documentation.html — Verarbeitung, FFprobe, Bild-/Audio-Encoder/Decoder; tatsächliche installierte Version und Codec-Lizenzen beachten.
- **Hugging Face Diffusers:** https://huggingface.co/docs/diffusers/en/api/pipelines/stable_diffusion/svd — technischer Kontext zu Video-Diffusionspipelines (keine Garantie für konkrete Cloud-Modelle).
- **Physikalische Videokonsistenz:** https://arxiv.org/abs/2607.04653 — Forschungsarbeit zu verbleibenden physikalischen Grenzen, methodische Einordnung statt Produktaussage.

## Open-Source-/Community-Ansätze (als Inspiration, nicht kopiert)

- **AI Film Director (BitraAI):** https://github.com/BitraAI/ai-film-director — Story → Drehbuch → Figuren → Locations/Props → Shotlist → Render/Audio; die öffentliche Repo-Ansicht nennt zum Recherchezeitpunkt **keine LICENSE-Datei**. Fremdcode daher nicht übernehmen.
- **AI Filmmaking Pipeline (JBORRAi):** https://github.com/JBORRAi/ai-filmmaking-pipeline — Blake/Blocking, 3D-Previz, Keyframe, Kostenerfassung und Pilot-Shot als Methode.
- **Narrascape:** https://github.com/zh683/narrascape — Stufenverträge, Timeline, QA und Rework-Kreislauf; Beta-Status laut öffentlicher Projektbeschreibung.
- **Film Production Skills:** https://github.com/zhangzhangco/film-production-skills — interoperable Stufen-/Agent-Skills und strukturierter Handoff.
- **Visual Storytelling Skills:** https://github.com/leynos/visual-storytelling-skills — Kontinuitätsextraktion, Referenzaufbau, Modellrouting, TTS.
- **StoryMind:** https://github.com/LinHao-city/StoryMind — shotorientierter Director mit demonstrierten kurzen Beispielen, Multi-Provider.
- **AI Cinematic Pipeline:** https://github.com/billpar/ai-cinematic-pipeline — konkrete Methodik für Shot-Design, Charakter-/Setting-Raster und Audio.
- **Everything AI Filmmaking:** https://github.com/MRCalderon3D/everything-ai-filmmaking — Referenzplanung, Keyframes, Continuity-Review, Edit-Plan.
- **Video Production Skills:** https://github.com/sb-dev/video-production-skills — Schwerpunkt auf Shot als kleinster wiederholbarer Einheit und getrennten Master-/Delivery-Artefakten.

## Was die Recherche NICHT belegt

- Dass jedes Modell seine Zahlenwerte für Brennweite/Kameragehäuse exakt physikalisch simuliert.
- Dass Referenzbilder/Seed/LoRA die gleiche Identität über einen langen Film mathematisch garantieren.
- Dass ein 1080p→4K-Upscale fehlerhafte Hände, Mimik oder Physik behebt.
- Dass man durch automatisierten Higgsfield-Zugang die Website-„Unlimited“-Regeln erhält.
- Dass jedes im Repo genannte öffentliche Drittprojekt ohne Lizenzprüfung kopiert oder kommerziell eingebettet werden darf.

**Technischer Risikohinweis:** Modelltarife, technische Limits und MCP-Skills entwickeln sich schnell. Der Operator ist vor jeder bezahlten Generierung für die Prüfung der tatsächlich angebundenen Version verantwortlich.
