# EP01-S002 | Die Stimme hinter der Tür | 5s

## Immutable identity and world constraints
Characters (same person in every frame, not similar-looking substitutes):
- MARA (Mara Neumann): Fiktive erwachsene Frau, 38, eckiges Gesicht mit kleiner Narbe über der linken Braue, dunkelbraunes kinnlanges Haar, graublaue Augen, natürliche Haut, glaubwürdige Proportionen. Wardrobe: dunkelgrauer wetterfester Mantel mit kleinem Messingreißverschluss, schwarze Stiefel, grauer Schal; über die gesamte Szene identisch. Voice: tiefe ruhige Frauenstimme, Deutsch, gehauchter Satz ohne theatralisches Kreischen.
Location CORRIDOR: Langer enger Korridor, grauer Putz, eine schwere Stahltür am Ende rechts im Bild; über der Tür eine gelbe Warnlampe; links freiliegende Kupferrohre; die ganze Zeit dieselben Türscharnier- und Griffpositionen
Time / world state: 23:40, Innenraum Nacht; Keine anderen Menschen, konstant kühle Luft, Warnleuchte über Tür
Props (exactly as referenced):
- Keine
Style bible: Fotorealistisch. Praktische Lichtquellen. Kühle Nachtfarben mit vereinzelten warmen Reflexen. Natürliche Hautstruktur, keine Beauty-Glättung. 35–65mm Äquivalent; ruhige präzise Kamerabewegungen.

## Dramatic purpose
Verzögerung vor dem Kontakt erzeugt Spannung.

## Visual blocking & movement
Detail von Maras rechter Hand, die sich langsam auf den kalten, festen Türgriff legt.
Performance: angespannt, aber beherrscht
Facial micro-expression: minimale Brauenbewegung, kein übertriebenes Schauspiel
Eyes: fixiert den Türgriff
Hands and gesture: rechte Hand, vier Finger sichtbar, Daumen auf der Gegenseite
Timing (seconds relative to THIS shot):
- 0s: Hand schwebt einen Zentimeter vor Griff
- 2s: Finger schließen sich um Metall
- 4s: kleine Drehung, Widerstand
Physics / anatomy / contacts: Die Hand bildet korrekte Fingerkurve um Griff; der starre Griff bewegt sich erst nach Drehung, keine durchdringenden Finger.

## Camera & light
Framing: extreme close-up of right hand and handle; focal length intent: 65mm full-frame equivalent
Camera height: 1.1m; axis side: south; screen direction: left_to_right
Movement: almost imperceptible push-in; stability: tripod; focus: skin-to-metal contact
Lens/shutter intent is guidance, NOT a promise of exact optical simulation.
Lighting: kaltes Oberlicht links, gelbe Türwarnlampe rechts; grade: kühles entsättigtes Grau, natürliche warme Hautreflexe; material/render: fotorealistische Hautporen, echter Stofffall, fein sichtbarer Staub

## Audio production cue (not assumed to be rendered)
Dialogue:
- Keine
Foley: Stoffrascheln, kleines metallisches Klicken
Ambient: fernes Brummen
Music: keine Musik in der Szene; Spannung durch Raumton
AUDIO POLICY: if native audio is available it is only a provisional track. Final mix is separately approved.

## Film continuity (MUST match the shot before/after)
At start: {'MARA': {'wardrobe': 'COAT_01', 'hand_left': 'empty', 'hand_right': 'empty', 'position': 'by_door', 'facing': 'east'}}
At end: {'MARA': {'wardrobe': 'COAT_01', 'hand_left': 'empty', 'hand_right': 'door_handle', 'position': 'by_door', 'facing': 'east'}}
Bridge type: direct; note: 

## Generation contract
Mode: image_to_video
Preferred providers/models (validate live capabilities and tariffs): higgsfield-available-i2v-model, comfyui-local
First frame: NOT APPROVED
Last frame: not specified
Additional references: none
Avoid: face swap, extra fingers, body morph, floaty motion, focal-length change, jump cuts, subtitles and logos
Do not invent characters, props, camera cuts, wardrobe, speech or physics not in the locked specification.
No extra action after the last beat. Preserve orientation, contact geometry, temporal order and face identity.
Generate ONLY this shot. One coherent movement per shot unless prescribed; no unintended cuts.

## Acceptance criteria
- Nur rechte Hand greift
- Kein deformierter Griff
- Physischer Widerstand sichtbar
