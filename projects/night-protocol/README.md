# Beispielproduktion: Nachtprotokoll — Episode 1

Fiktiver Thriller, 33 Sekunden, sechs einstellungsbasierte Shots in einem fixierten Set. Die Spezifikation enthält dieselbe Figur, denselben Mantel, eine nachvollziehbare Türmechanik, Kameraachse, Blicklinie, Geräusch- und Dialogvorgaben. Sie zeigt außerdem einen Cutaway-Shot, ohne die Szene zeitlich zu brechen.

**Absichtlich unvollständig:** Bildreferenzen, Startframes, Rechtefreigabe, Audio-Master und tatsächliche Videos fehlen. `shotloom preflight` muss daher blockieren. Die vorbereiteten Prompts und Jobs werden mit `shotloom compile` generiert.

Start: `shotloom validate --project projects/night-protocol`; danach `shotloom compile --project projects/night-protocol --episode EP01`.

Assets gehören in `assets/characters/mara/`, `assets/locations/`, `assets/props/`. Der Nutzer/Director muss diese Bilder freigeben und jedem I2V-Shot einen Startframe zuweisen. Anschließend erneut kompilieren. Unkontrollierte Generierung ist nicht das Ziel dieser Demo.
