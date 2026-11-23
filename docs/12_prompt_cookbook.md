# 12 — Providerneutrale Promptrezepte und praktische Beispiele

## Systemprompt für die Regie-KI

> Du bist Filmregisseur, Showrunner und Production Supervisor. Lies Projekt-Bible und bestehende Freigaben als nicht verhandelbare Fakten. Erstelle für jede Szene einen kausalen Handlungsbogen und eine räumlich verständliche Shotliste. Jede Einstellung hat eine genaue Absicht, ein Bewegungs-/Physikprotokoll, Identitätsanker, Lichtregeln, einen einzigen primären Kameramove, dramaturgische Audio-Cues und konkrete Abnahmekriterien. Übersetze nur die darstellungsrelevanten Aspekte in die tatsächliche Provider-Promptsprache; ändere keine Geschichte, Identität oder Handlungen. Generiere erst mit echter Freigabe und prüfe die Outputs. Bei Fehler: Ursache, kleinste Korrektur, Budget-/Freigabestatus. Keine behaupteten Ergebnisse ohne tatsächliche Renderdatei.

## Character Lock (Wiederverwendung in jedem relevanten Shot)

> Same exact pre-approved character ID `MARA`, not a lookalike: [reference-front], [reference-threequarter], [reference-profile], [reference-fullbody]. Preserve anatomical left eyebrow scar, hairline, eye shape, body proportions, visible skin microtexture, wardrobe ID `COAT_01`, shoe material and seams. The emotion changes, the actor identity does not. No face morphing, no invented accessories.

Nicht als magische „perfect consistency“-Garantie betrachten. Stattdessen freigegebene tatsächliche Dateien und Shotbewertung verwenden.

## Physical Action Lock

> At 0.0 s the right hand approaches the fixed metal handle. At 1.8 s the thumb contacts the back side and fingers wrap around the front. At 2.5 s the handle rotates a small amount against mechanical resistance; the door does not move yet. At 3.8 s the latch releases; only then can the door open on its fixed hinge. Keep the same handle geometry and stable contact points until release. No teleporting, no joint deformation, no free-floating fingers.

## Cinematography Lock

> Camera south of the east–west action axis. Eye-level 1.55 m, 50 mm full-frame equivalent framing intent. Static close-up; single subtle focus change from eyes to the handle. Door remains frame right; warning lamp above the door. No orbit, no cut within the shot, no reverse-angle axis jump. Natural perspective and realistic parallax; not a demand for simulated physical lens metadata.

## Performance Lock

> She notices a faint metallic click, pauses for 0.4 s, holds breath briefly, raises her gaze by a few degrees and tightens the jaw. The face remains calm but tense; no theatrical screaming or sudden eyebrow animation. Eye movement precedes small head movement. The left hand stays outside the frame without changing object possession.

## Spatial and Material Lock

> Narrow corridor with copper pipes frame left, steel door frame right, yellow warning lamp above it. Practical cool overhead lamp is the primary soft light; warning lamp adds warm localized reflections. Matte wall plaster, steel handles and textured coat each respond differently to light; material identity persists between frames.

## Dialogue / Audio Lock

> Dialogue audio event at 2.0 s: MARA whispers exact German text „Das war meine Stimme.“ One breath beforehand, no additional words. Preserve phoneme timing if the selected model supports verified audio/visual conditioning; otherwise generate the approved voice track separately and lipsync only after image continuity is stable. Ambient electrical hum abruptly stops after the last word; keep spatial reverberation consistent with the narrow corridor.

## Negative Constraints – fachlich statt generisch

> Exclude: any extra character, unplanned camera cut, new prop, distorted fingers, unanchored feet, geometry changes, face identity switch, clothing substitution, impossible object penetration, changing door hinge, phantom audio dialog, subtitles or watermarks generated into the scene.

*Providerhinweis:* Nicht jeder Anbieter hat ein eigenständiges Negative-Prompt-Feld. Solche Angaben nur in unterstützter Syntax verwenden; anderenfalls als natural-language constraints im Hauptbrief einbauen.

## Zwei-Modell-Workflow für schweres Material

1. Mit Bildmodell ein genehmigtes Static mit exakter Person, Set und Bildkomposition erstellen.
2. Optional gleichwertiges Endframe aus Story-/Raumfakten erstellen.
3. Mit I2V-/Reference-Modell kleine kontrollierte Bewegung ergänzen.
4. Wenn Fokus auf Dialog liegt, ggf. separaten Voice-/Lip-Sync-Workflow; wenn Fokus auf Bewegung liegt, reale Motion-Referenz oder 3D-Kontrollbild.
5. Ausgang mit QA gegen echte Referenzen vergleichen.

## Sparregel

Kleinerer zuverlässiger Shot und sehr guter Schnitt schlagen einen überladenen 20-Sekunden-KI-Take, bei dem jede Sekunde eine Figur verändert. Kurze Cutaways, echte Reaktionsshots, räumlich verankerte Tonereignisse und Story-begründete Perspektivenwechsel sind produktive Stilmittel – keine Fehlerverdeckung.
