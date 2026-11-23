# 02 — Filmsprache: Kamera, Bild, Licht, Bewegung und Erzählung

## Erst Dramaturgie, dann Bild

Jeder Shot beantwortet: Wer erlebt was? Welche Information/Emotion verändert sich? Was soll der Zuschauer als Nächstes erwarten? Ein schöner Kameramove ohne erzählerische Funktion ist keine Qualität. Kontrast auf Szenenebene: Distanz → Nähe, Stille → Bewegung, weites Set → Detail, Blick → Reaktion. Ein Schnitt darf Raum, Zeit oder Bedeutung verändern – aber nicht unbeabsichtigt Verwirrung erzeugen.

## Einstellungsgrößen / Wirkung

- Extreme Wide/Establishing: Ort, Isolation, Größenverhältnisse und Geografie; braucht erkennbare Landmarken.
- Wide/Full: komplette Körpermechanik, Füße, Kontakte und Raum; schwerer für KI, daher kontrollierte Bewegung.
- Medium/Over Shoulder: Beziehungen, Reaktionen, körperliche Handlung; Schulterseite und 180°-Achse fixieren.
- Close-Up: Mimik, Blick, Blicke zur relevanten Person/Gegenstand; Schärfeebene auf Augen und natürliche Mikrogesten.
- Extreme Close-Up/Insert: Hand-Objekt-Kontakt, Textur, Schalter, Uhr; nur wenn Objektform/Handzahl wirklich stimmen.
- POV: Wissenszustand der Figur; Seh-/Kamerahöhe und Blickrichtung konsistent.

**Brennweiten als ästhetische Absicht**, bezogen auf Vollformat: 24–35 mm für Raum und Nähe, 40–65 mm für natürliche Halbnahe/Porträts, 85 mm+ für selektive Portraittrennung. Extreme Weitwinkel erzeugen Verzerrungen. Sensorgröße, tatsächliche Kamera, Blende, Fokusabstand und digitale Bearbeitung beeinflussen die reale Perspektive; generative Modelle befolgen numerische Brennweiten nicht zwangsläufig.

## Kameraachsen und Bewegungen

Eine Szene braucht ein räumliches Koordinatensystem und festgelegte Bewegungsrichtung. Achte auf die 180°-Regel: Kamera bleibt auf einer Seite der Handlungsachse, es sei denn ein motivierter, sichtbarer Achsenwechsel etabliert die neue Orientierung. Die Blickrichtung A→B muss in der Gegeneinstellung passen. Verlasse dich **nicht** auf „move left“ im Prompt allein: benenne statische Landmarken und nutze Keyframes/Blender.

Camera move recipes:

| Bewegung | Geschätzte Wirkung | Technische Vorsicht |
|---|---|---|
| Lock-off | Spannung durch Schauspiel / Erwartung | ideal für Lippen-/Handdetails |
| Dolly push | Steigende Wichtigkeit | keine FOV-/Gesichtsänderung hineinprompten |
| Side tracking | Räumlicher Weg | Landmarken und Parallaxe kontrollieren |
| Tilt/pan | Informationsenthüllung | keine erfundenen Objekte im offscreen Raum |
| Orbit | Enthüllung / Machtbeziehung | besonders driftanfällig, möglichst 3D-Kontrollbild |
| Handheld | unmittelbare Präsenz | nur geringe, motivierte Abweichung; kein zufälliges Schütteln |

**Grundsatz:** Eine Hauptbewegung pro Shot. Kamera kann statisch sein, während Motiv handelt. Bewegungen nicht gleichzeitig „crane up, zoom in, roll 180°, orbit 360°, fast whip pan“ kombinieren, wenn die Handlung physikalisch verständlich sein soll.

## Komposition, Optik, Belichtung

Beschreibe: Vordergrund, Mitte, Hintergrund; Headroom, Leadroom, Negativraum; Bildeinstieg/-ausstieg; Subjektgröße; Blicklinie; Tiefenstaffelung; Fokusziel und Fokuswechsel. Für glaubhafte Optik: Schatten konsistent zur Anzahl/Richtung der Lichtquellen; Reflexionen wandern nachvollziehbar; Kontaktschatten unter Füßen; Belichtungssprünge motiviert; Hautstruktur statt Plastik; Körnung sparsam; kein ungewolltes Flickern. Depth of field dient dem Motiv – künstlich zu starker Bokeh-Brei macht Setkontinuität schlechter.

## Farbe und Kontinuität

`look_lock` ist ein wiederholbares Look-Dokument: Weißabgleich, Farbhierarchie, Hauttöne, Kontrastumfang, dominante Farbtemperatur, Tageszeit, Lichtquellen und Materialpalette. Erst auf Shotebene konsistent generieren, danach alle Clips auf gemeinsame Referenz graden. AI-Grading kann einzelne Frames verschieden interpretieren: im Motion-Review auf Color/Pulsing achten. Für den Standardexport Rec.709 SDR festlegen, nur echte HDR-/10bit-Workflows als solche deklarieren.

## Realismus wird durch Nebendinge sichtbar

Lichter spiegeln sich in Augen und Metall in korrekter Richtung; Kleidung reagiert verzögert auf Bewegung; Schritte erzeugen vertikale Schwerpunktverschiebung; Strähnen folgen Kopfbewegung; Hände greifen ein Objekt an plausibler Stelle; Objekte verändern nicht ihre Materialklasse; Wasser folgt Gravitation und Kontakt; Schatten bleiben an Licht gebunden. Diese Details werden als *beobachtbare Akzeptanzkriterien* formuliert, nicht als Adjektivliste.

## Schnitt: Anschluss vor Effekt

Schneide auf Bewegung oder Blick, wenn Handlungen räumlich nachvollziehbar sein sollen. Etabliere Blickachse und Reaktionsshot; halte Handlungskontinuität (Hand am Griff vor Schnitt → Hand am Griff nach Schnitt) und Screen Direction. Ein Insert kann Zeit überspringen, darf aber nicht stillschweigend Kostüm, Raum oder Gegenstand verändern. Plane vor dem Render 0,5–1 s Handlungs-Haltemöglichkeit pro Seite, soweit der Anbieter und Budget es erlauben. „Handles“ in `episodes/*.yaml` sind derzeit Planungsmetadaten, nicht automatisch zusätzlich gerenderte Sekunden.

## Photorealistischer Shot-Prompt: Minimum

1. **Subjekt** (freigegebene Identität + Kleidung + aktueller Zustand).
2. **Wo** (Set-Geometrie, Tageszeit, Lichtquellen).
3. **Was passiert** (ein Primärereignis, Kausalität, Beats mit relativen Sekunden).
4. **Wie handelt die Person** (Augen, Gesichtsmuskeln, Atem, Hände, Gewicht).
5. **Wie sieht es die Kamera** (Bildgröße, Standort/Achse, Blickrichtung, ein Move, Fokus).
6. **Welche physikalischen Kontakte** müssen über die Dauer halten?
7. **Welche Geräusche/Sätze** sind Synchronisationsevents, nicht stilistisches Beiwerk?
8. **Was darf sich nicht ändern** und was sind messbare Review-Kriterien?

> Nicht mehr Worte um ihrer selbst willen schreiben. Ein zu langer widersprüchlicher Prompt verschlechtert Präzision. Die Wahrheit liegt in freigegebenen Referenzen, Keyframes, nachvollziehbaren Zuständen und einem funktionierenden Kontrollprozess.
