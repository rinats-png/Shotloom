# 08 — Einwilligung, Rechte, Datenschutz, Produktionskosten und sichere Automatisierung

## Rechts-/Einwilligungs-Gate

Vor Veröffentlichung oder bezahltem Rendern mit sensiblen hochgeladenen Assets: Quelle, Person, Erlaubnis, Verwendungszweck, Plattform, Laufzeit und kommerzielle Nutzbarkeit prüfen. Für Gesichter/Stimmen realer Menschen eine passende Einwilligung/rechtliche Grundlage; keinen Identitätsdiebstahl und keine falschen Testimonials/Deepfake-Impersonation. Bei Kindern besonders restriktiv, bei markenrechtlichen Filmen Logos/Produkte/geschützte Designs separat klären. Musik, SFX, Stockmaterial, Fonts, 3D-Assets und Trainings-/Fintuningbilder sind eigenständige Rechtequellen. „Aus KI“ bedeutet nicht automatisch gemeinfrei. Bei Werbe-/Dokuformaten Tatsachen prüfen und ggf. synthetische Inhalte angemessen kennzeichnen.

`projects/<slug>/rights/assets.csv` ist eine Vorlage für Asset-Provenienz. Nur wenn sämtliche für den konkreten Film nötigen Rechte/Einwilligungen geklärt sind, `project.policy.rights_cleared=true`. Die CLI prüft **das Flag**, nicht juristisch jede einzelne Lizenz – nicht mit einer automatischen Rechtsprüfung verwechseln.

## Privatsphäre

API-Schlüssel und OAuth-Tokens niemals in Projektdateien, Prompts, Git oder Supportlogs. Bilder von Privatpersonen nicht ohne Einwilligung an externe Cloud-Anbieter senden. Vertrags- und Datenstandortfrage beim gewählten Modell/provider beurteilen. Sensible Originaldaten nach Freigabe möglichst begrenzt vorhalten und Metadaten/EXIF für Veröffentlichungen bewusst entfernen. Bei Teams Zugriffsrechte, Rollen und sichere Backups etablieren.

## Finanzielles Risikomanagement

Projektbudget `max_total`, Versuchslimit `max_per_attempt`, Reservequote `planning_reserve_pct`. Eine Episode mit 10 geplanten Clips kann nach QA mehrere Wiederholungen erfordern. Kalkuliere **erwartete Versuche** statt nur die Anzahl finaler Clips. Beispiel (kein Anbieterpreis): 6 Shots × 2,5 Versuche × 2 € = 30 €, plus 25 % Reserve = 37,50 €. Audio, Bilder, Upscale, Speicher, Schnitt, Provider-Abos und menschliche Arbeit getrennt ausweisen. Reale Tarife zur Laufzeit abrufen.

`authorize` reserviert eine Maximalsumme je Shot, `record` verbucht tatsächliche Kosten. Eine Freigabe ist nicht die Erlaubnis für unbegrenzt viele weitere Versuche. Wenn ein Versuch seine genehmigte Summe ausgeschöpft hat, neue explizite Freigabe einholen. Der Verbrauch wird lokal geführt, ist **kein** Ersatz für die Rechnungsansicht des Anbieters. Bei manuellen Website-Gutschriften ebenfalls tatsächliche Credits dokumentieren; das heutige Ledger arbeitet nur mit vereinbartem EUR/USD-Betrag.

## Zahlungen und Agenten

Der CLI-Schalter `--confirmed` beweist nicht, dass ein Mensch bestätigt hat. Ein autonomer Agent könnte ihn missbrauchen. Für ein kommerzielles Produkt sind serverseitig autorisierte, revisionssichere Freigaben und verifizierte Provider-Kosten nötig. Im lokalen Workflow dürfen Agenten den Schalter **nur** nach einer eindeutig protokollierten Nutzerzustimmung einsetzen. Ohne diese Zustimmung kein bezahlter Provider-Aufruf.

## Veröffentlichungs-Gate

Vor Release: End-to-end-Review, Ton-/Bildkontrolle, Rechte-/Einwilligungsmatrix, Plattformformat, Assetquellen, Offenlegungspflichten, Archivierung, Feedback/Revisionsrecht. Kein automatischer Veröffentlichungsklick aus einem ungesichteten Render.
