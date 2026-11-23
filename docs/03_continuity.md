# 03 — Identität und Continuity über Shots, Szenen und Episoden

## Einmalige Identitätsdaten

Jeder Mensch trägt eine stabile ID (z. B. `MARA`), niemals einen in Shots generierten neuen Namen. Referenzpaket: frontales Portrait mit neutralem Ausdruck, ¾, beide Profile wo Asymmetrie wichtig ist, Ganzkörper mit Kleidung, eindeutige Detailansicht, optional kurze reale Bewegungsreferenz (nur mit Erlaubnis). Freigaben mit Hash, Erstelldatum, Modell/Quelle und Rechten vermerken. Identitäts-Lock beschreibt möglichst beobachtbare Details: Augenfarbe, markante Asymmetrie, Haaransatz, Kleidungsmaterial, Schuhform, ungefähre Proportionen und Hauttextur. Nicht unrealistische Adjektive wie „perfekt identisch“ als alleinige Technik verwenden.

Für eine Serienfigur zusätzlich `voice_lock`, Gangart, typische Reaktionen, Biografie, private Motive, Verhaltensgrenzen, Veränderungsbogen und Timeline der Kleidung. Identität ≠ Kleidungszustand ≠ Schauspielzustand: drei getrennte Felder, damit eine legitime Kostümänderung nicht als neues Gesicht generiert wird.

## Continuity-Ledger

Pro Shot sind `continuity.entry` und `continuity.exit` Datenobjekte: Position, Blickrichtung, linke/rechte Hand, Kleidung, getragene Requisiten und relevanter Zustand. Beim direkt anschließenden nächsten Shot müssen die dokumentierten Zustände übereinstimmen. Bei Schwenk nach Offscreen, Zeitellipse oder Insert `bridge: cutaway|time_jump|reset` mit Begründung dokumentieren – nicht verwenden, um echte Fehler zu kaschieren.

Beispiel:

```yaml
continuity:
  entry:
    MARA:
      wardrobe: COAT_01
      hand_left: empty
      hand_right: door_handle
      position: by_door
      facing: east
  exit:
    MARA:
      wardrobe: COAT_01
      hand_left: empty
      hand_right: empty
      position: threshold
      facing: east
  bridge: direct
  note: "Tür wurde innerhalb des Shots geöffnet"
```

## Geografie wird nicht improvisiert

Hinterlege eine Raumkarte: Wand/Öffnung/Fenster/Spiegel/Einrichtung in Weltkoordinaten, Norden/Osten, Kameraachse, vorherrschende Lichtquellen, Gehwege, Sichtlinien. Ein langer Flur darf nicht in der Gegeneinstellung zu zwei parallelen Türen werden. Markiere Requisitpositionen explizit (inklusive linke/rechte Seite relativ zur Person, nicht nur zum Bildschirm). Bei komplexem Blocking ein 3D-Greybox in Blender mit echter Kamera oder Photogrammetrie, nicht nur Text.

## Abdeckung vor Generation prüfen

- Alle `character_ids`, `prop_ids`, `location_id`, `scene_id` existieren.
- Im Moment des Sprechens ist die Figur sichtbar oder ausdrücklich eine Off-Stimme. Der aktuell eingebaute Validator fordert sichtbare Sprecher und muss für Off-Stimmen später erweitert werden.
- Der Schnitt hat ausreichende Anschlussbilder (Establishing, Reaktionen, Inserts, motivierte Close-ups).
- Jede Bewegung von links nach rechts und jede Blickachse ist auf einem Achsenplan dokumentiert.
- Zustand von Hand, Requisite, Türöffnung, Verletzung, Schmutz und Wetter ist vor und nach einer Aktion nachvollziehbar.

## Wichtige Grenze des Validators

Die Software prüft heute IDs, statische Achsenzuordnung, Dialog-/Beat-Timing und einige `entry`/`exit`-Schlüssel. Sie kann nicht visuell beweisen, dass eine Nase identisch ist, ein Blick richtig sitzt oder das Licht physikalisch korrekt fällt. Das muss in G7 ein Reviewer am Video prüfen. Der Kreativvertrag-Hash macht genehmigte generierte Versuche bei Projekt-/Skriptänderung unselektierbar und verhindert eine Montage mit veraltetem Inhalt; derzeit betrifft er bewusst alle Shots der Episode.

## Referenzplanung

Besonders schwierige Shots (Gesicht im Profil, Handfläche, Rückseitenwechsel, Spiegel, Nässe, starke Parallaxe) erhalten zusätzliche spezielle Referenzen. Für einen Blickwechsel mehrere Start-End-Keyframes verwenden. Für dynamische Aktionen reale Video-/Skelettreferenz, Pose-/Depth-/ControlNet-Workflow falls Provider tatsächlich unterstützt. Keine nicht nachweisbare „ID-Garantie“ behaupten.

## Serienstaffeln

Erstelle nach jeder Episode eine `continuity/season-ledger.yaml` mit Datum, erlernten Fakten, Verletzungen, Kostümänderungen, Motivationsänderungen, Familienbeziehungen, offenen Setups und Payoffs. Ein späteres Drehbuch muss diese Daten berücksichtigen. Wiederkehrende Orte und Stimmen bleiben unverändert, solange die Story explizit eine Änderung begründet.
