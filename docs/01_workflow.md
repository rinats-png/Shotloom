# 01 — Produktionsworkflow: von Idee zu Episode oder Film

## Einsatzformen

Kurzfilm, Serienepisode, Mehrteiler, Trailer, Werbefilm, Musikvideo, Dokumentation, Social-Ad: dieselbe Orchestrierung mit anderen dramaturgischen Zielen. Nicht alle Formate benötigen Dialog oder Figuren. Der Showrunner setzt zuerst `project.format`, danach Laufzeit, Verhältnis, Auslieferung und Produktionsbudget. Für nichtfiktionale Projekte sind überprüfbare Tatsachen, Archivlizenzen und Quellen Pflicht.

## G0 — Brief und Produktionsvertrag

Der Nutzer darf frei sprechen. Extrahiere: Warum soll das Video existieren? Wer schaut es? Emotionaler Zielzustand, Genre, Ton, Story-Kern, Figuren, Orte, Laufzeit, Ausspielung, Sprache, Realismusgrad, Tabus, Budget, vorhandene Referenzen und Anbieterzugang. Fehlt etwas, fülle unverbindliche kreative Annahmen und vermerke es in `notes.md` als **Annahme**. Keine Einwilligungen, Rechtslage oder Kostenannahmen erfinden. Ergebnis: `project.yaml` + Konflikt-/Fragenliste (maximal echte Blocker).

## G1 — Dramaturgie, Drehbuch, Beat Sheet

Schreibe zuerst Logline (Protagonist + Ziel + Hindernis + Einsatz). Für eine Episode: cold open, Setup, auslösendes Ereignis, Progression/Komplikation, Wendung, Entscheidung, Payoff/Cliffhanger. Für einen 20-s-Trailer: Hook, Besonderheit, Eskalation, emotionaler Payoff, Absender. Plane mindestens eine verständliche Ursache-Wirkung-Kette; jede Szene muss eine Information, Beziehung oder Lage ändern. Dialog nicht als Erklärung benutzen, wenn Bilder/Handlung reichen. **Erst nach G1:** Shotzählung und visuelle Komplexität schätzen.

## G2 — Narrative/visuelle/akustische Bible

Für wiederkehrende Menschen: stabile ID, frontales Gesicht, ¾ und Profil, Ganzkörper, Kleidung und Schuhwerk, markante Asymmetrien, Körperproportionen, natürliche Hauttextur, Stimme/Sprechweise, typische Gesten. Generiere genehmigte Referenzen **vor** Sequenzen. Für Orte: Grundriss mit markierten Türen/Fenstern/Möbeln und Lichtquellen. Für Requisiten: Inventar, exakte Form und Handhabung. Eigene Varianten über IDs `WARDROBE_01`, `LOCATION_02`, `PROP_03` statt stiller Überschreibung. Ergebnis: `project.yaml`, `assets/`, `rights/assets.csv`.

## G3 — Blocking, Storyboard, Coverage

Für jede Szene Raumachsen festlegen, Objektstandorte einzeichnen, Reihenfolge der Handlungen beschreiben. Dann Shots planen: ID, zeitlicher Beat, Subjekt, Bildgröße, Brennweitenintention, Höhe, Kamerabewegung, Blickachse, Staging, Emotion, Audioereignisse und Übergänge. Deckung prüfen: Gibt es ein Establishing? Wessen Perspektive ist die Szene? Kann der Zuschauer die Aktion räumlich verstehen? Sind Reaktionen und Inserts vorhanden? Gibt es einen sinnvollen Match-on-Action? Setze Shotdauer nach Handlung, nicht nach Modell-Maximaldauer. Ergebnisse: `episodes/*.yaml`, `compile` erzeugt Shot-Prompts und Timeline.

## G4 — Keyframes und Vorvisualisierung

1. Für jeden dynamischen Shot ein Konzept-Still und meist freigegebenen Startframe erzeugen.
2. Bei Zustandswechsel zusätzlich Endframe (z. B. geschlossene → geöffnete Tür). **Endframe unabhängig anhand der Bible erstellen**, nicht blind aus einem fehlerhaften Frame weitergenerieren.
3. Für kritische Perspektive/Physik 3D-Greybox in Blender oder echte Referenzaufnahme. Echte Kamera/Objektivgeometrie ist ein besserer Kontrollrahmen als Textwünsche wie „35mm“.
4. Die Referenzbilder visuell auf Identität/Set/Griffkontakte prüfen. Alle Bilder mit stabilen IDs im Projekt registrieren.
5. Referenzlimits des tatsächlich gewählten Modells im Tool prüfen; bei Limits pro Shot gezielt die wichtigsten Bilder verwenden, statt eine Garantie zu erfinden.

## G5 — Vorprüfung und Budget

`shotloom validate`: statische Fehler, IDs, Dialogtiming, Achsenbrüche, grobe Zustandskontinuität. `shotloom preflight`: Rechte, Bilddateien, erforderlicher Startframe und Renderfreigaben. Daneben macht der Operator echte Modell-/Preisprüfung: Auflösung, Dauer, Audio, Ein- und Ausgabe, Latenz und realistische Anzahl Versuche. **Erst reale Nutzerfreigabe für einen maximalen Betrag pro Shot**, keine globale „autonome Kostenberechtigung“.

## G6 — Rendering pro Shot

Zuerst einen schwierigsten **Pilot-Shot end-to-end** produzieren und validieren. Nicht sofort 20 Shots bezahlen. Jobs aus `compiled/<episode>/jobs/` lesen. Ein Auftrag = ein Shot = ein Renderversuch. Übergib freigegebene Bilder/Keyframes und präzisen Prompt über offizielles Higgsfield CLI/MCP oder anderes Tool. Save original file, provider/version, Konfiguration, Kosten, Referenzen; `record` protokolliert Hash und Versuch. Wenn Anbieter nur eine Weboberfläche bietet, manuell generieren und Datei importieren; niemals einen Fake-API-Aufruf vortäuschen.

## G7 — QA und gezielte Nacharbeit

Prüfe Vollbild in Originalauflösung, Video in Echtzeit und bei Einzelbildkontrolle: Identität, Anatomie, Kontakt, Gewicht, Zeitverlauf, Bildrichtung, Licht, Stimme, Artefakte, Emotionalität. `review` mit allen zehn Kriterien; bei Fehlern genaue Zeitmarke und Fehlerklasse. Wenn nur Lip-Sync falsch ist, Sound/Dialogue-Pfad prüfen, nicht gesamten Look neu erfinden. Wenn die Tür durch Hände geht, Body/Grip-Blocking oder Set-Keyframe ersetzen. `select` darf ausschließlich geprüfte Versuche markieren. Auswahl ist nicht endgültige Filmfreigabe.

## G8 — Schnitt, Ton, Farbe, Master

Erstelle Audio-Edit-Decision-List aus `compiled/.../timeline.json`. Dialog zuerst sauber aufnehmen/erzeugen, Töne synchron zum tatsächlichen Footage platzieren, Roomtone über Schnitte führen, Foley/Kontakt einsetzen, Musik dramaturgisch passend unterlegen. Falls generiertes Originalvideo bereits Ton hat: prüfen, ggf. Stems gewinnen oder nachsynchronisieren. Schnitt auf Handlung und Emotion, nicht auf „jeweils 5 Sekunden“. `shotloom assemble` erzeugt derzeit ein normiertes Rohmaster mit harten Cuts und separat gemastertem Audiotrack (oder explizit stumm). Komplexe Überblendungen/J-/L-Cuts/Color-Grading weiterhin mit NLE/DAW durchführen oder später als verifizierte CLI-Module ergänzen. Untertitelentwurf ist ungeprüft.

## G9 — Veröffentlichung

End-to-end Master in echter Wiedergabe anschauen und auf Geräten der Zielplattform testen. Prüfbericht inkl. letzten Frames, Schrift-/Safe Areas, Untertitel, Lautheit und Rechte führen. Originale, verifizierte Export-/Providerdateien und Manifest archivieren. `shotloom release` protokolliert die erklärte menschliche Schlussabnahme, ersetzt sie aber nicht. Keine Veröffentlichung, solange kritische Fehler oder Lizenzzweifel offen sind.

## Operator-Check nach jedem Gate

`Was ist belastbar fertig?` → `Welche geprüften Artefakte gibt es?` → `Welche IDs sind noch blockiert?` → `Welche Kosten sind verbucht und maximal freigegeben?` → `Was ist die EINE nächste Aktion?`.

**Anti-Pattern:** Ungeduldig auf den „Film erzeugen“-Button drücken, bevor die Charakterreferenzen stimmen. Das macht jede spätere Korrektur teuer.
