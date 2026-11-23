# 05 — Audio, Sprache, Geräusche, Sounddesign, Schnitt und Auslieferung

## Ton planen, bevor ein Bild generiert wird

Ein Film besteht nicht aus „Video plus Musik“, sondern hörbaren Ursachen, Perspektive und Raum. Jede Szene bekommt eine **akustische Geografie**: Welche Quelle ist wo, welche Entfernungen/Reflexionen, was hört die Figur, was nur das Publikum? Dialog/Handlungsgeräusche müssen an exakt bestimmten Bewegungen hängen. Definiere in jedem Shot die primären Audio-Cues und Priorität: Stimme vor Foley vor Raum vor Musik, sofern dramaturgisch nichts anderes gewollt ist.

## Stimmen und Schauspiel

1. Für jede Figur eine `voice_lock`: Sprache, Akzent, Tempo, Artikulation, Textur, Höhenlage, Atem, Lautstärke, emotionale Einschränkungen. Bei identischer Serienfigur nicht pro Episode eine neue Stimmpersönlichkeit erzeugen.
2. Schauspieltext VOR Video präzisieren (Interpunktion, Sprechtempo, Pausen, emotionaler Subtext). Für anspruchsvollen Lipsync Audio zuerst aufnehmen/erzeugen und dann das entsprechende Tool wählen.
3. Sprecherrechte dokumentieren: keine fremden Stimmen ohne Zustimmung imitieren, Voice-Clone nur mit ausreichender Freigabe.
4. Bei nativem generiertem Audio: Phoneme, Konsonantenwechsel, Pausen, Sprachverständlichkeit, Atem und Lautheitsverlauf prüfen; falsche Sprache oder Zusatzaussagen verwerfen.
5. Für ADR/Lipsync: Aufnahmen konsolidieren, an Clip-Frames ausrichten und sichtbare Lippen bei 100%-Wiedergabe beurteilen. Nicht aus Untertitel-Timing auf echte Phonemsynchronität schließen.

## Soundeffekte/Foley

Geräusche sind physikalische Beweise. Eine Tür mit Metallgewicht muss akustische Trägheit, Scharnier, Aufprall und Raumantwort haben. Schritte folgen sichtbaren Bodenkontakten, Kleidung reagiert auf Bewegung, ein Griff klingt beim Widerstand anders als beim Loslassen. Foley als separate editierbare Stems mit Herkunft/License führen. Sound darf eine visuelle Unmöglichkeit nicht „heilen“ – er kann aber eine subtile physikalisch plausible Bewegung glaubwürdiger machen.

## Soundscape

Baue Basisebenen: Raumton/Kontinuität (möglichst nahtlos über Cuts), punktuelle Objekt-SFX, ggf. Außenatmo, perspektivische Stimmen, Dramaturgie-/Musiklayer. Beim J-Cut beginnt Ton vor dem Bildwechsel; beim L-Cut läuft Ton über ihn hinaus. Mit diesen Varianten wirken Sequenzen weniger wie zusammengeklebte Kurzclips. Raumklang und Hall an konkreten Locations ausrichten; keine wahllose Hallfahne.

## Mixing

- In 48-kHz-Projekt bleiben; in Stereo oder geplantes Mehrkanalformat mischen.
- Sprache verständlich, kein Pumpen durch Noise-Reduction; Musik unter Dialog kontrollieren; Übersteuerungen vermeiden.
- Ziel-Loudness und True-Peak-Limit **pro Plattform und Lieferauftrag** festlegen. Es gibt keinen universell korrekten LUFS-Wert für Kino, Broadcast, Social Media und Werbung.
- Musik-/SFX-Urheberrechte und Nutzungsrechte dokumentieren; generierte Musik ebenfalls providerabhängig lizenzieren.
- Mit Kopfhörern, Lautsprechern und Handy gegenhören; Mono-Kompatibilität prüfen, wenn relevant.
- Erhalte ein separates freigegebenes Audio-Master als WAV, bevor `shotloom assemble` ausgeführt wird. Native Tonspur der Videoclips wird von der aktuellen Minimal-Assembly **nicht automatisch** in den Mix übernommen.

## Montage / Editorial

Baue eine Edit-Decision-List (EDL) aus Shot-IDs, Start-/Endzeiten, Auswahlversuch und Übergang. Die `compiled/EPxx/timeline.json` ist Ausgangspunkt. Schneide nicht blind nach im Voraus geplanten 5 Sekunden, wenn das beste Schauspiel nur in 3,8 Sekunden liegt. Gegenwärtig wird für eine einfache Montage jeder ausgewählte Clip auf die geplante Shotdauer zugeschnitten und in ein einheitliches FPS-/Auflösungsformat kodiert. Bei fehlender Clipdauer kann die FFmpeg-Assembly die erwartete Dauer ggf. nicht füllen; deshalb nach dem Export die tatsächliche Laufzeit prüfen. Komplexe Montage mit Fade, Retiming, Audio-Stems, Titles, Mehrspur-Color ist ein NLE-Auftrag oder ein späteres Modul.

## Untertitel

`shotloom subtitles` generiert eine erste SRT-Schätzung aus den geplanten Dialogstarts. Die Zeiten sind **nicht** phonetisch aus finalem Ton ausgerichtet. Vor Auslieferung Dialogtranskript überprüfen, Timing an das tatsächliche Master anlegen, Zeichensetzung, Lesedauer und Safe-Area prüfen. Für Mehrsprachigkeit separates Sprach-/Untertitelpaket pro Sprache. Untertitel nicht unfreiwillig als Teil eines Videomodellprompts erzeugen lassen, wenn das Tool keine zuverlässige Textkontrolle hat.

## Auslieferungsprofile

- Master: gewünschtes Seitenverhältnis, korrekte Pixelgröße/FPS, Farbraum, Videocodec, Audiocodec und feste Start-/End-Zeit.
- Versionen: 16:9, 9:16, 1:1 nur als **eigene Kompositionen**, nicht blind zentrieren; Köpfe/Action nachführen.
- Trailer/Teaser: gesonderte dramaturgische Schnittfassung, keine willkürliche Teilfolge.
- Protokoll: Prüfsumme, verwendete Shots, Kosten, Rechte, freigegebene Sprache, Untertitel, Datum und Version.

## QC-Tonliste

Kratzt/clippt etwas? Sind die Worte verständlich, natürlich und vollständig? Hörbare Stille bewusst? Sind Schritte/Griff/SFX synchron? Gleiche Stimmen in allen Episoden? Unsichtbare Brüche durch Raumton kaschiert oder neu bearbeitet? Musiklizenz und Audiofreigabe dokumentiert? Ausgabe auf Smartphone und Kopfhörer geprüft?
